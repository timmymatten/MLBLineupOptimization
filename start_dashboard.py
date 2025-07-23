"""
File: start_dashboard.py
Description: Smart startup script that finds an available port and launches the dashboard
This handles port conflicts automatically (like macOS AirPlay on port 5000)
"""

import socket
import webbrowser
import time
import sys
from app import app

def find_free_port(start_port=5001, max_port=5020):
    """Find a free port starting from start_port"""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise OSError("No free ports found in range")

def main():
    try:
        # Find an available port
        port = find_free_port()
        
        print("=" * 60)
        print("🚀 MLB Lineup Optimization Dashboard")
        print("=" * 60)
        print(f"✓ Found available port: {port}")
        print(f"✓ Dashboard URL: http://localhost:{port}")
        print(f"✓ API Base URL: http://localhost:{port}/api")
        print("=" * 60)
        print("📊 Dashboard Features:")
        print("  • Interactive team selection")
        print("  • Real-time lineup optimization")
        print("  • Evolution progress tracking")
        print("  • Performance visualization")
        print("=" * 60)
        print("🔧 Troubleshooting:")
        print("  • Check browser console (F12) for errors")
        print("  • Ensure data/batting_stats.csv exists")
        print("  • Run 'python check_data.py' for diagnostics")
        print("=" * 60)
        
        # Update the API base in the HTML file if needed
        update_dashboard_port(port)
        
        # Start the Flask app
        print(f"🌐 Starting server on port {port}...")
        print("💡 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Auto-open browser after a short delay
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(f'http://localhost:{port}')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start Flask app
        app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check if all required files exist")
        print("2. Run 'python check_data.py' for diagnostics")
        print("3. Ensure Python dependencies are installed")
        sys.exit(1)

def update_dashboard_port(port):
    """Update the API base URL in the dashboard HTML"""
    try:
        # Read the current dashboard.html
        with open('dashboard.html', 'r') as f:
            html_content = f.read()
        
        # Replace the API base URL
        old_api_base = "const API_BASE = 'http://localhost:5001/api';"
        new_api_base = f"const API_BASE = 'http://localhost:{port}/api';"
        
        if old_api_base in html_content:
            html_content = html_content.replace(old_api_base, new_api_base)
            
            # Write back to file
            with open('dashboard.html', 'w') as f:
                f.write(html_content)
            
            print(f"✓ Updated dashboard.html to use port {port}")
        
    except Exception as e:
        print(f"⚠ Could not update dashboard.html: {e}")
        print(f"💡 Manually change API_BASE to 'http://localhost:{port}/api' in dashboard.html")

if __name__ == "__main__":
    main()