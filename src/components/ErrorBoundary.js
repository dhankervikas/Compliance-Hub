import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Uncaught Error:", error, errorInfo);
        this.setState({ error, errorInfo });
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="p-8 bg-red-50 min-h-screen font-sans">
                    <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-lg border border-red-200">
                        <h1 className="text-2xl font-bold text-red-700 mb-4">Something went wrong.</h1>
                        <p className="mb-4 text-gray-700">The application encountered an unexpected error.</p>

                        <div className="bg-gray-100 p-4 rounded overflow-auto mb-4 border border-gray-300">
                            <h2 className="font-semibold text-gray-900">Error:</h2>
                            <pre className="text-red-600 text-sm whitespace-pre-wrap">{this.state.error && this.state.error.toString()}</pre>
                        </div>

                        <div className="bg-gray-100 p-4 rounded overflow-auto border border-gray-300">
                            <h2 className="font-semibold text-gray-900">Component Stack:</h2>
                            <pre className="text-gray-600 text-xs whitespace-pre-wrap">{this.state.errorInfo && this.state.errorInfo.componentStack}</pre>
                        </div>

                        <button
                            onClick={() => window.location.href = '/'}
                            className="mt-6 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                        >
                            Return to Home
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
