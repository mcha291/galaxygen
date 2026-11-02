import { Component, type ReactNode } from "react";

import { Button } from "./Button";
import { Dialog } from "./Dialog";
import { StatusDot } from "./StatusDot";

interface Props {
  /** Changing this clears a caught error: a new checkpoint or view is a fresh try. */
  resetKey: string;
  children: ReactNode;
}

interface State {
  error: Error | null;
  key: string;
  /** The fault's dialog closed: the line in the view's place still says it. */
  dismissed: boolean;
}

/**
 * Contain a crashing view, so one bad plot does not blank the workflow beside it. The fault is said in the design
 * system's Dialog (T17, S84) - what failed and the next action, Retry - and, once that is closed, by the line where
 * the view stood.
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null, key: this.props.resetKey, dismissed: false };

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { error, dismissed: false };
  }

  static getDerivedStateFromProps(props: Props, state: State): Partial<State> | null {
    return props.resetKey !== state.key ? { error: null, key: props.resetKey, dismissed: false } : null;
  }

  render() {
    const { error, dismissed } = this.state;
    if (!error) return this.props.children;
    const retry = () => this.setState({ error: null, dismissed: false });
    return (
      <>
        <p role={dismissed ? "alert" : undefined} style={{ margin: "var(--space-5)", font: "var(--text-data)", color: "var(--status-fault)" }}>
          <StatusDot tone="fault" style={{ marginRight: "var(--space-3)" }} />
          This view failed: {error.message}. Change the checkpoint or view to retry.
        </p>
        <Dialog
          open={!dismissed}
          role="alertdialog"
          label="Fault"
          title="This view failed"
          width={420}
          onClose={() => this.setState({ dismissed: true })}
          footer={
            <Button variant="primary" onClick={retry}>
              Retry
            </Button>
          }
        >
          <p style={{ margin: 0, font: "var(--text-data)", color: "var(--status-fault)", overflowWrap: "anywhere" }}>{error.message}.</p>
          <p style={{ margin: "var(--space-4) 0 0", fontSize: "var(--size-sm)" }}>Retry draws it again; another checkpoint or view is a fresh try too.</p>
        </Dialog>
      </>
    );
  }
}
