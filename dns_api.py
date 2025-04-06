from flask_cors import CORS
from flask import Flask, request, jsonify
import socket
import dns.resolver

app = Flask(__name__)
CORS(app)

def get_dns_records(domain: str) -> dict:
    """Get DNS records for a domain."""
    result = {
        "domain": domain,
        "ipAddress": "",
        "nameServers": [],
        "cloudflareNameServers": False
    }

    try:
        # Get IP address
        result["ipAddress"] = socket.gethostbyname(domain)

        # Get NS records
        ns_records = dns.resolver.resolve(domain, 'NS')
        result["nameServers"] = [ns.to_text() for ns in ns_records]

        # Check for Cloudflare name servers
        cloudflare_ns = {'dns1.cloudflare.net.', 'dns2.cloudflare.net.',
                        'dns3.cloudflare.net.', 'dns4.cloudflare.net.'}
        result["cloudflareNameServers"] = any(
            ns in cloudflare_ns for ns in result["nameServers"]
        )

    except socket.gaierror:
        result["ipAddress"] = "Error: Domain could not be resolved."
    except dns.resolver.NoAnswer:
        result["nameServers"] = ["No NS records found"]
    except dns.resolver.NXDOMAIN:
        result["nameServers"] = ["Domain does not exist"]
    except Exception as e:
        result["nameServers"] = [f"Error: {str(e)}"]

    return result

@app.route('/dns-lookup', methods=['GET'])
def dns_lookup():
    """API endpoint to fetch DNS records."""
    domain = request.args.get('domain')
    if not domain:
        return jsonify({"error": "Domain parameter is required"}), 400
    
    records = get_dns_records(domain)
    return jsonify(records)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)