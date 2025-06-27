import socket
import multiprocessing
import time
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(processName)s - %(message)s')

def start_server(port, server_name):
    """Start a TCP server listening on the specified port."""
    try:
        # Create a TCP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow port reuse to avoid "Address already in use" errors
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind to localhost and the specified port
        server_socket.bind(('localhost', port))
        # Listen for connections (max 5 queued)
        server_socket.listen(5)
        logging.info(f"{server_name} listening on port {port}")

        # Keep the server running (accept connections but do nothing for this test)
        while True:
            client_socket, addr = server_socket.accept()
            client_socket.close()  # Immediately close connection for simplicity
    except Exception as e:
        logging.error(f"{server_name} failed on port {port}: {e}")
    finally:
        server_socket.close()

def main():
    # Define ports and server names
    servers = [
        (8001, "TestServer1"),
        (8002, "TestServer2"),
        (8003, "TestServer3"),
    ]

    # Start each server in a separate process
    processes = []
    for port, name in servers:
        process = multiprocessing.Process(target=start_server, args=(port, name), name=name)
        process.daemon = True  # Ensure processes terminate when main process exits
        processes.append(process)
        process.start()

    # Keep the main process running to allow testing
    try:
        logging.info("All test servers started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)  # Keep main process alive
    except KeyboardInterrupt:
        logging.info("Shutting down test servers...")
        for process in processes:
            process.terminate()
            process.join()

if __name__ == "__main__":
    main()
