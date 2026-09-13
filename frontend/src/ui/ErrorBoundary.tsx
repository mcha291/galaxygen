import { Component, type ReactNode } from "react";

interface Props {
  /** Changing this clears a caught error: a new checkpoint or view is a fresh try. */
  resetKey: string;
  children: ReactNode;
}

interface State {
  error: Error | null;
  key: string;
}

/** Contain a crashing view, so one bad plot does not blank the workflow beside it. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null, key: this.props.resetKey };

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { error };
  }

  static getDerivedStateFromProps(props: Props, state: State): Partial<State> | null {
    return props.resetKey !== state.key ? { error: null, key: props.resetKey } : null;
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <p role="alert" style={{ margin: "var(--space-5)", font: "var(--text-data)", color: "var(--status-fault)" }}>
        This view failed: {this.state.error.message}. Change the checkpoint or view to retry.
      </p>
    );
  }
}
