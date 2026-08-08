import React from 'react';

// Catches any render/lifecycle error in its child tree and shows a message
// instead of letting React silently unmount the whole app to a blank page.
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // This is exactly what to check in the browser console (F12) when
    // something goes blank - this log is the real error, every time.
    console.error('Caught by ErrorBoundary:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h2>Something went wrong loading this page.</h2>
          <p style={{ color: '#666' }}>{this.state.error?.message}</p>
          <button onClick={() => window.location.href = '/'}>Go back home</button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;