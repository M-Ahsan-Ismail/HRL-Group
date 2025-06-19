from odoo import http
from odoo.http import request

class PaySLip_API(http.Controller):
    @http.route('/pay/slip/api', type='json', auth='public', methods=['GET', 'POST'])
    def get_payslip_data_via_api(self):
        employee_id = request.env.user.employee_id
        if not employee_id:
            return {'error': 'No employee linked to this user'}

        slip_recs = request.env['hr.payslip'].sudo().search([
            ('employee_id', '=', employee_id.id),
        ])

        slip_data = [{
            'employee_name': slip.employee_id.name,
            'date_from': slip.date_from.strftime('%Y-%m-%d') if slip.date_from else None,
            'date_to': slip.date_to.strftime('%Y-%m-%d') if slip.date_to else None,
            'reference': slip.name,
            'payslip_id': slip.id,
        } for slip in slip_recs]

        # For type='json' routes, return a Python dict/list directly
        return {'status': 'success', 'data': slip_data}

    @http.route('/pay/slip/test', type='http', auth='user', methods=['GET'])
    def payslip_test_page(self):
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head><title>PaySlip Test</title></head>
        <body>
            <h1>PaySlip API Test</h1>
            <button onclick="fetchPayslips()">Load PaySlips</button>
            <div id="result"></div>

            <script>
            function fetchPayslips() {
    document.getElementById('result').innerHTML = 'Loading...';
    
    fetch('/pay/slip/api', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {},
            id: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        let html = '';
        
        if (data.result && data.result.status === 'success') {
            html += `<h2>✅ Found ${data.result.data.length} PaySlip(s)</h2>`;
            
            data.result.data.forEach((slip, index) => {
                html += `
                    <div style="border: 2px solid #007bff; margin: 15px 0; padding: 15px; border-radius: 8px; background: #f8f9fa;">
                        <h3 style="color: #007bff; margin-top: 0;">PaySlip #${index + 1}</h3>
                        <p><strong>👤 Employee:</strong> ${slip.employee_name}</p>
                        <p><strong>📄 Reference:</strong> ${slip.reference}</p>
                        <p><strong>📅 Period:</strong> ${slip.date_from} to ${slip.date_to}</p>
                        <p><strong>🆔 PaySlip ID:</strong> ${slip.payslip_id}</p>
                    </div>
                `;
            });
        } else if (data.result && data.result.error) {
            html += `<div style="color: red; padding: 10px; border: 1px solid red; border-radius: 5px;">
                ❌ Error: ${data.result.error}
            </div>`;
        } else {
            html += '<div style="color: orange;">⚠️ Unexpected response format</div>';
            html += '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
        
        document.getElementById('result').innerHTML = html;
    })
    .catch(error => {
        document.getElementById('result').innerHTML = `
            <div style="color: red; padding: 10px; border: 1px solid red; border-radius: 5px;">
                ❌ Network Error: ${error.message}
            </div>
        `;
    });
}
            </script>
        </body>
        </html>
        '''
        return html_content

