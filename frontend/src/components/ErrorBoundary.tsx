import { Component, type ErrorInfo, type ReactNode } from 'react';

type Props = {
  children: ReactNode;
};

type State = {
  hasError: boolean;
};

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Global UI error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="panel error-fallback">
          <h2>Something went wrong</h2>
          <p>The app hit an unexpected issue. Please refresh and try again.</p>
        </div>
      );
    }

    return this.props.children;
  }
}
