from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
from pathlib import Path
from credential_generator_branded import CredentialPDFGeneratorBranded
import tempfile
import traceback
import requests

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# reCAPTCHA Configuration
RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY', '')  # Frontend key
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY', '')  # Backend secret key
RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'
RECAPTCHA_THRESHOLD = 0.5  # Score threshold (0.0-1.0, higher = stricter)

# Create temp directory for uploads
UPLOAD_FOLDER = tempfile.mkdtemp(prefix='sony_')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def verify_recaptcha(recaptcha_token):
    """Verify reCAPTCHA token with Google servers"""
    if not RECAPTCHA_SECRET_KEY:
        # If reCAPTCHA not configured, log warning but allow request
        print("Warning: RECAPTCHA_SECRET_KEY not configured")
        return True

    try:
        response = requests.post(
            RECAPTCHA_VERIFY_URL,
            data={
                'secret': RECAPTCHA_SECRET_KEY,
                'response': recaptcha_token
            },
            timeout=5
        )

        result = response.json()

        # Check if verification was successful
        if not result.get('success'):
            return False

        # Check score (v3 returns score 0.0-1.0)
        score = result.get('score', 0)
        if score < RECAPTCHA_THRESHOLD:
            print(f"reCAPTCHA score too low: {score}")
            return False

        return True
    except Exception as e:
        print(f"reCAPTCHA verification error: {str(e)}")
        # Fail open - allow request if verification service is down
        return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/download-template')
def download_template():
    """Download Excel template"""
    try:
        template_path = os.path.join(Path(__file__).parent, 'templates', 'Credential_Template.xlsx')
        if os.path.exists(template_path):
            return send_file(template_path, as_attachment=True, download_name='Credential_Template.xlsx')
        else:
            return jsonify({'error': 'Template not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview-records', methods=['POST'])
def preview_records():
    """Get filtered records for preview and selection"""
    try:
        data = request.json
        filename = data.get('filename')
        search_name = data.get('search_name', '').strip()
        selected_roles = data.get('selected_roles', [])
        selected_delegations = data.get('selected_delegations', [])
        sort_order = data.get('sort_order', 'none')

        if not filename:
            return jsonify({'success': False, 'error': 'No filename provided'}), 400

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 400

        df = pd.read_excel(filepath)
        filtered_df = df.copy()

        # Apply filters
        if search_name:
            search_lower = search_name.lower()
            mask = (filtered_df['Name first'].str.lower().str.contains(search_lower, na=False) |
                   filtered_df['Name last/family'].str.lower().str.contains(search_lower, na=False))
            filtered_df = filtered_df[mask]

        if selected_roles:
            filtered_df = filtered_df[filtered_df['Role'].isin(selected_roles)]

        if selected_delegations:
            filtered_df = filtered_df[filtered_df['Delegation'].isin(selected_delegations)]

        # Apply sorting
        if sort_order == 'alphabetical':
            filtered_df = filtered_df.sort_values(['Name last/family', 'Name first']).reset_index(drop=True)
        elif sort_order == 'reverse':
            filtered_df = filtered_df.sort_values(['Name last/family', 'Name first'], ascending=False).reset_index(drop=True)

        # Build preview data
        records = []
        for idx, row in filtered_df.iterrows():
            records.append({
                'index': int(idx),
                'first_name': str(row.get('Name first', '')),
                'last_name': str(row.get('Name last/family', '')),
                'role': str(row.get('Role', '')),
                'sport': str(row.get('Sports', '')),
                'delegation': str(row.get('Delegation', ''))
            })

        return jsonify({
            'success': True,
            'records': records,
            'total': int(len(df)),
            'filtered': int(len(filtered_df))
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/validate-file', methods=['POST'])
def validate_file():
    """Validate uploaded Excel file structure with detailed error messages"""
    try:
        # Verify reCAPTCHA token
        recaptcha_token = request.form.get('recaptcha_token', '')
        if not verify_recaptcha(recaptcha_token):
            return jsonify({
                'success': False,
                'error': 'reCAPTCHA verification failed',
                'suggestion': 'Please try again or contact support if the problem persists'
            }), 403

        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'suggestion': 'Please select an Excel file to upload'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'suggestion': 'Please choose a file before uploading'
            }), 400

        # Check file extension
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'error': 'Invalid file format',
                'suggestion': 'Please upload an Excel file (.xlsx or .xls)',
                'action': 'download_template'
            }), 400

        # Save temporarily
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Validate structure
        try:
            df = pd.read_excel(filepath)

            # Check if file is empty
            if len(df) == 0:
                return jsonify({
                    'success': False,
                    'error': 'Excel file is empty',
                    'suggestion': 'Please add participant data to the spreadsheet',
                    'action': 'download_template'
                }), 400

            required_cols = ['Name first', 'Name last/family', 'Role', 'Sports', 'Delegation']
            actual_cols = df.columns.tolist()

            # Check for missing columns
            missing_cols = [col for col in required_cols if col not in actual_cols]

            if missing_cols:
                # Try to provide helpful suggestions
                suggestions = []
                for missing in missing_cols:
                    close_match = None
                    for actual in actual_cols:
                        if missing.lower() == actual.lower():
                            close_match = actual
                            break
                    if close_match:
                        suggestions.append(f'"{missing}" (found as "{close_match}" - note the exact spelling matters)')
                    else:
                        suggestions.append(f'"{missing}"')

                return jsonify({
                    'success': False,
                    'error': f'Missing required columns: {", ".join(missing_cols)}',
                    'required_columns': required_cols,
                    'found_columns': actual_cols,
                    'suggestions': suggestions,
                    'note': 'Column names are case-sensitive. Make sure the spelling matches exactly.',
                    'action': 'download_template'
                }), 400

            # Validate data quality
            validation_warnings = []

            # Check for empty cells in required columns
            for col in required_cols:
                empty_count = df[col].isna().sum() + (df[col] == '').sum()
                if empty_count > 0:
                    validation_warnings.append(f'⚠️ {col}: {empty_count} empty cells found')

            # Check for duplicate names
            full_names = df['Name first'].astype(str) + ' ' + df['Name last/family'].astype(str)
            duplicates = full_names[full_names.duplicated()].unique()
            if len(duplicates) > 0:
                validation_warnings.append(f'⚠️ Found {len(duplicates)} duplicate names')

            # Check minimum records
            if len(df) < 1:
                return jsonify({
                    'success': False,
                    'error': 'No participant records found',
                    'suggestion': 'Please add at least one participant to the spreadsheet'
                }), 400

            # Get filter options
            roles = sorted([str(r).strip() for r in df['Role'].unique() if pd.notna(r)])
            delegations = sorted([str(d).strip() for d in df['Delegation'].unique() if pd.notna(d)])

            # Calculate complete records - convert numpy types to Python int for JSON serialization
            empty_cell_counts = [int(df[col].isna().sum()) + int((df[col] == '').sum()) for col in required_cols]
            max_empty = int(max(empty_cell_counts)) if empty_cell_counts else 0
            total_records = int(len(df))
            complete_records = total_records - max_empty

            return jsonify({
                'success': True,
                'filename': file.filename,
                'rows': total_records,
                'columns': df.columns.tolist(),
                'roles': roles,
                'delegations': delegations,
                'warnings': validation_warnings,
                'data_quality': {
                    'total_records': total_records,
                    'complete_records': complete_records
                }
            })

        except Exception as e:
            error_msg = str(e).lower()
            if 'no columns to parse' in error_msg or 'empty data' in error_msg:
                suggestion = 'The file appears to be empty or corrupted. Please download the template and add your data.'
                action = 'download_template'
            else:
                suggestion = 'Unable to read the Excel file. Please ensure it is a valid Excel format.'
                action = 'download_template'

            return jsonify({
                'success': False,
                'error': f'Invalid Excel file: {str(e)}',
                'suggestion': suggestion,
                'action': action
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'suggestion': 'An unexpected error occurred. Please try again.'
        }), 500

@app.route('/api/generate-credentials', methods=['POST'])
def generate_credentials():
    """Generate credential PDFs with optional filtering and record selection"""
    try:
        data = request.json

        # Verify reCAPTCHA token
        recaptcha_token = data.get('recaptcha_token', '')
        if not verify_recaptcha(recaptcha_token):
            return jsonify({
                'success': False,
                'error': 'reCAPTCHA verification failed',
                'suggestion': 'Please try again or contact support if the problem persists'
            }), 403

        filename = data.get('filename')
        event_name = data.get('event_name', 'Special Olympics Event')
        event_type = data.get('event_type', 'Summer')
        sizing_preset = data.get('sizing_preset', 'standard')

        # Get filter parameters
        search_name = data.get('search_name', '').strip()
        selected_roles = data.get('selected_roles', [])
        selected_delegations = data.get('selected_delegations', [])
        sort_order = data.get('sort_order', 'none')
        selected_indices = data.get('selected_indices', [])  # Specific record selection

        if not filename:
            return jsonify({'success': False, 'error': 'No filename provided'}), 400

        # Load the Excel file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 400

        df = pd.read_excel(filepath)

        # Apply filters
        filtered_df = df.copy()

        # Filter by name (search)
        if search_name:
            search_lower = search_name.lower()
            mask = (filtered_df['Name first'].str.lower().str.contains(search_lower, na=False) |
                   filtered_df['Name last/family'].str.lower().str.contains(search_lower, na=False))
            filtered_df = filtered_df[mask]

        # Filter by roles
        if selected_roles:
            filtered_df = filtered_df[filtered_df['Role'].isin(selected_roles)]

        # Filter by delegations/regions
        if selected_delegations:
            filtered_df = filtered_df[filtered_df['Delegation'].isin(selected_delegations)]

        # Apply sorting
        if sort_order == 'alphabetical':
            filtered_df = filtered_df.sort_values(['Name last/family', 'Name first']).reset_index(drop=True)
        elif sort_order == 'reverse':
            filtered_df = filtered_df.sort_values(['Name last/family', 'Name first'], ascending=False).reset_index(drop=True)

        # If specific records are selected, filter to only those
        if selected_indices:
            filtered_df = filtered_df.iloc[selected_indices].reset_index(drop=True)

        if len(filtered_df) == 0:
            return jsonify({
                'success': False,
                'error': 'No records selected. Please select at least one record to generate credentials.'
            }), 400

        # Generate PDF
        generator = CredentialPDFGeneratorBranded(event_name, event_type, sizing_preset)
        output_path = os.path.join(UPLOAD_FOLDER, f'credentials_{event_type.lower()}_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        generator.generate(filtered_df, output_path)

        return jsonify({
            'success': True,
            'pdf_file': os.path.basename(output_path),
            'credentials_count': int(len(filtered_df)),
            'total_records': int(len(df)),
            'filtered': int(len(df)) > int(len(filtered_df)) or len(selected_indices) > 0
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<pdf_file>')
def download_pdf(pdf_file):
    """Download generated PDF"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, pdf_file)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404

        return send_file(filepath, as_attachment=True, mimetype='application/pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Azure uses port 8000
    # debug=False for production
    app.run(host='0.0.0.0', port=8000, debug=False)
