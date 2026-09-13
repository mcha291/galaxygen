/* @ds-bundle: {"format":4,"namespace":"GalaxyDesignSystem_658871","components":[{"name":"Badge","sourcePath":"components/core/Badge.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"Card","sourcePath":"components/core/Card.jsx"},{"name":"Dialog","sourcePath":"components/core/Dialog.jsx"},{"name":"IconButton","sourcePath":"components/core/IconButton.jsx"},{"name":"Tabs","sourcePath":"components/core/Tabs.jsx"},{"name":"Tag","sourcePath":"components/core/Tag.jsx"},{"name":"Tooltip","sourcePath":"components/core/Tooltip.jsx"},{"name":"DataTable","sourcePath":"components/data/DataTable.jsx"},{"name":"Meter","sourcePath":"components/data/Meter.jsx"},{"name":"Readout","sourcePath":"components/data/Readout.jsx"},{"name":"SPRITE_URL","sourcePath":"components/data/StarIcon.jsx"},{"name":"SPECTRAL_COLORS","sourcePath":"components/data/StarIcon.jsx"},{"name":"CORES","sourcePath":"components/data/StarIcon.jsx"},{"name":"MODIFIERS","sourcePath":"components/data/StarIcon.jsx"},{"name":"StarIcon","sourcePath":"components/data/StarIcon.jsx"},{"name":"StatusDot","sourcePath":"components/data/StatusDot.jsx"},{"name":"Checkbox","sourcePath":"components/forms/Checkbox.jsx"},{"name":"Input","sourcePath":"components/forms/Input.jsx"},{"name":"Select","sourcePath":"components/forms/Select.jsx"},{"name":"Switch","sourcePath":"components/forms/Switch.jsx"}],"sourceHashes":{"components/core/Badge.jsx":"e793322a0720","components/core/Button.jsx":"5318613b343d","components/core/Card.jsx":"b7cd8f7212dd","components/core/Dialog.jsx":"3428a02507cc","components/core/IconButton.jsx":"23104896487b","components/core/Tabs.jsx":"daf00a1adc62","components/core/Tag.jsx":"3ebbe6adefd6","components/core/Tooltip.jsx":"07ea103b08af","components/data/DataTable.jsx":"18d855eda71a","components/data/Meter.jsx":"01dfbdcd4c8e","components/data/Readout.jsx":"983ae5922691","components/data/StarIcon.jsx":"ca484ecc7232","components/data/StatusDot.jsx":"1e7d6980620e","components/forms/Checkbox.jsx":"51c1c03da43e","components/forms/Input.jsx":"c9f21705f45e","components/forms/Select.jsx":"c0fbff891704","components/forms/Switch.jsx":"734a4f49691d","ui_kits/atlas/AtlasShell.jsx":"001b2f25c16b","ui_kits/atlas/CatalogScreen.jsx":"33c84d5a3875","ui_kits/atlas/ObjectScreen.jsx":"268a10d66dea","ui_kits/atlas/SurveyScreen.jsx":"2e44c91e4381","ui_kits/atlas/catalog-data.js":"fa7d606c94b4"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.GalaxyDesignSystem_658871 = window.GalaxyDesignSystem_658871 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/core/Badge.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const TONES = {
  neutral: {
    color: 'var(--text-muted)',
    background: 'var(--surface-2)',
    border: 'var(--border-hair)'
  },
  nominal: {
    color: 'var(--aqua-2)',
    background: 'var(--status-nominal-bg)',
    border: 'var(--aqua-5)'
  },
  caution: {
    color: 'var(--amber-2)',
    background: 'var(--status-caution-bg)',
    border: 'var(--amber-5)'
  },
  fault: {
    color: 'var(--coral-2)',
    background: 'var(--status-fault-bg)',
    border: 'var(--coral-5)'
  },
  archive: {
    color: 'var(--violet-2)',
    background: 'var(--status-archive-bg)',
    border: 'var(--violet-5)'
  },
  accent: {
    color: 'var(--magenta-2)',
    background: 'var(--surface-selected)',
    border: 'var(--magenta-5)'
  }
};

/** Small status label. Mono, uppercase, hairline-bordered. */
function Badge({
  tone = 'neutral',
  children,
  ...rest
}) {
  const t = TONES[tone];
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      height: 18,
      padding: '0 var(--space-3)',
      font: 'var(--text-label)',
      letterSpacing: 'var(--track-label)',
      textTransform: 'uppercase',
      borderRadius: 'var(--radius-xs)',
      color: t.color,
      background: t.background,
      border: '1px solid ' + t.border,
      whiteSpace: 'nowrap'
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Badge.jsx", error: String((e && e.message) || e) }); }

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const VARIANTS = {
  primary: {
    background: 'var(--magenta-3)',
    color: 'var(--text-inverse)',
    border: '1px solid var(--magenta-3)'
  },
  secondary: {
    background: 'var(--surface-2)',
    color: 'var(--text-primary)',
    border: '1px solid var(--border-line)'
  },
  ghost: {
    background: 'transparent',
    color: 'var(--text-body)',
    border: '1px solid transparent'
  },
  danger: {
    background: 'transparent',
    color: 'var(--coral-2)',
    border: '1px solid var(--coral-4)'
  }
};
const HOVER = {
  primary: {
    background: 'var(--magenta-2)',
    borderColor: 'var(--magenta-2)'
  },
  secondary: {
    background: 'var(--surface-hover)',
    borderColor: 'var(--border-strong)'
  },
  ghost: {
    background: 'var(--surface-hover)',
    color: 'var(--text-primary)'
  },
  danger: {
    background: 'var(--status-fault-bg)',
    color: 'var(--coral-1)'
  }
};
const SIZES = {
  sm: {
    height: 'var(--control-sm)',
    padding: '0 var(--space-4)',
    fontSize: 'var(--size-xs)'
  },
  md: {
    height: 'var(--control-md)',
    padding: '0 var(--space-5)',
    fontSize: 'var(--size-sm)'
  },
  lg: {
    height: 'var(--control-lg)',
    padding: '0 var(--space-7)',
    fontSize: 'var(--size-base)'
  }
};

/** Primary action control. Verb labels, sentence case, one or two words. */
function Button({
  variant = 'secondary',
  size = 'md',
  disabled = false,
  fullWidth = false,
  iconLeft,
  iconRight,
  onClick,
  children,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const [down, setDown] = React.useState(false);
  return /*#__PURE__*/React.createElement("button", _extends({
    type: "button",
    disabled: disabled,
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => {
      setHover(false);
      setDown(false);
    },
    onMouseDown: () => setDown(true),
    onMouseUp: () => setDown(false),
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 'var(--space-3)',
      width: fullWidth ? '100%' : 'auto',
      fontFamily: 'var(--font-ui)',
      fontWeight: 'var(--weight-medium)',
      letterSpacing: '0.01em',
      borderRadius: 'var(--radius-md)',
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.4 : 1,
      transition: 'var(--transition-control)',
      whiteSpace: 'nowrap',
      transform: down && !disabled ? 'translateY(1px)' : 'none',
      ...SIZES[size],
      ...VARIANTS[variant],
      ...(hover && !disabled ? HOVER[variant] : null)
    }
  }, rest), iconLeft, children, iconRight);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/Card.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Hairline panel. Galaxy's default container — no drop shadow. */
function Card({
  title,
  label,
  actions,
  padding = 'var(--space-5)',
  children,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("section", _extends({
    style: {
      background: 'var(--surface-card)',
      border: '1px solid var(--border-hair)',
      borderRadius: 'var(--radius-md)',
      boxShadow: 'var(--shadow-inset)',
      overflow: 'hidden'
    }
  }, rest), title || label || actions ? /*#__PURE__*/React.createElement("header", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-4)',
      padding: 'var(--space-4) var(--space-5)',
      borderBottom: '1px solid var(--border-hair)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 0
    }
  }, label ? /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-label)',
      letterSpacing: 'var(--track-label)',
      textTransform: 'uppercase',
      color: 'var(--text-muted)',
      marginBottom: 2
    }
  }, label) : null, title ? /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-h3)',
      color: 'var(--text-primary)'
    }
  }, title) : null), actions) : null, /*#__PURE__*/React.createElement("div", {
    style: {
      padding
    }
  }, children));
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Card.jsx", error: String((e && e.message) || e) }); }

// components/core/IconButton.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const SIZES = {
  sm: 24,
  md: 32,
  lg: 40
};

/** Square icon-only control for toolbars and rails. Requires a label for a11y. */
function IconButton({
  label,
  size = 'md',
  selected = false,
  disabled = false,
  onClick,
  children,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const px = SIZES[size];
  return /*#__PURE__*/React.createElement("button", _extends({
    type: "button",
    "aria-label": label,
    title: label,
    disabled: disabled,
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      width: px,
      height: px,
      display: 'grid',
      placeItems: 'center',
      borderRadius: 'var(--radius-md)',
      background: selected ? 'var(--surface-selected)' : hover && !disabled ? 'var(--surface-hover)' : 'transparent',
      border: '1px solid ' + (selected ? 'var(--border-accent)' : 'transparent'),
      color: selected ? 'var(--magenta-2)' : hover ? 'var(--text-primary)' : 'var(--text-muted)',
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.4 : 1,
      transition: 'var(--transition-control)',
      padding: 0
    }
  }, rest), children);
}
Object.assign(__ds_scope, { IconButton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/IconButton.jsx", error: String((e && e.message) || e) }); }

// components/core/Dialog.jsx
try { (() => {
/** Modal overlay. The only element that blurs the canvas behind it. */
function Dialog({
  open,
  title,
  label,
  footer,
  width = 480,
  onClose,
  children
}) {
  if (!open) return null;
  return /*#__PURE__*/React.createElement("div", {
    role: "dialog",
    "aria-modal": "true",
    "aria-label": typeof title === 'string' ? title : undefined,
    style: {
      position: 'fixed',
      inset: 0,
      zIndex: 100,
      display: 'grid',
      placeItems: 'center',
      background: 'var(--scrim)',
      backdropFilter: 'var(--blur-md)',
      padding: 'var(--space-7)'
    },
    onClick: onClose
  }, /*#__PURE__*/React.createElement("div", {
    onClick: e => e.stopPropagation(),
    style: {
      width: '100%',
      maxWidth: width,
      background: 'var(--surface-1)',
      border: '1px solid var(--border-strong)',
      borderRadius: 'var(--radius-lg)',
      boxShadow: 'var(--shadow-3)',
      animation: 'none'
    }
  }, /*#__PURE__*/React.createElement("header", {
    style: {
      display: 'flex',
      alignItems: 'flex-start',
      gap: 'var(--space-4)',
      padding: 'var(--space-5) var(--space-5) var(--space-4)',
      borderBottom: '1px solid var(--border-hair)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 0
    }
  }, label ? /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-label)',
      letterSpacing: 'var(--track-label)',
      textTransform: 'uppercase',
      color: 'var(--text-muted)',
      marginBottom: 4
    }
  }, label) : null, /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-h3)',
      color: 'var(--text-primary)'
    }
  }, title)), /*#__PURE__*/React.createElement(__ds_scope.IconButton, {
    label: "Close",
    size: "sm",
    onClick: onClose
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 14,
      lineHeight: 1
    }
  }, "\xD7"))), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-5)',
      color: 'var(--text-body)'
    }
  }, children), footer ? /*#__PURE__*/React.createElement("footer", {
    style: {
      display: 'flex',
      justifyContent: 'flex-end',
      gap: 'var(--space-3)',
      padding: 'var(--space-4) var(--space-5)',
      borderTop: '1px solid var(--border-hair)'
    }
  }, footer) : null));
}
Object.assign(__ds_scope, { Dialog });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Dialog.jsx", error: String((e && e.message) || e) }); }

// components/core/Tabs.jsx
try { (() => {
/** Underline tab bar. Selected tab carries the magenta rule. */
function Tabs({
  items = [],
  value,
  onChange
}) {
  const [hover, setHover] = React.useState(null);
  return /*#__PURE__*/React.createElement("div", {
    role: "tablist",
    style: {
      display: 'flex',
      gap: 'var(--space-7)',
      borderBottom: '1px solid var(--border-hair)'
    }
  }, items.map(it => {
    const on = it.value === value;
    return /*#__PURE__*/React.createElement("button", {
      key: it.value,
      role: "tab",
      "aria-selected": on,
      onClick: () => onChange && onChange(it.value),
      onMouseEnter: () => setHover(it.value),
      onMouseLeave: () => setHover(null),
      style: {
        background: 'none',
        border: 0,
        padding: '0 0 var(--space-4)',
        cursor: 'pointer',
        display: 'inline-flex',
        alignItems: 'center',
        gap: 'var(--space-3)',
        fontFamily: 'var(--font-ui)',
        fontSize: 'var(--size-sm)',
        fontWeight: on ? 'var(--weight-medium)' : 'var(--weight-regular)',
        color: on ? 'var(--text-primary)' : hover === it.value ? 'var(--text-body)' : 'var(--text-muted)',
        boxShadow: 'inset 0 -1px 0 ' + (on ? 'var(--magenta-3)' : 'transparent'),
        transition: 'var(--transition-control)'
      }
    }, it.label, it.count != null ? /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--font-mono)',
        fontSize: 'var(--size-2xs)',
        color: 'var(--text-faint)'
      }
    }, it.count) : null);
  }));
}
Object.assign(__ds_scope, { Tabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Tabs.jsx", error: String((e && e.message) || e) }); }

// components/core/Tag.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Removable metadata chip — filters, spectral classes, survey labels. */
function Tag({
  children,
  onRemove,
  color,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  return /*#__PURE__*/React.createElement("span", _extends({
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 'var(--space-2)',
      height: 22,
      padding: '0 var(--space-3)',
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--size-xs)',
      color: 'var(--text-body)',
      background: 'var(--surface-2)',
      borderRadius: 'var(--radius-xs)',
      border: '1px solid ' + (hover ? 'var(--border-line)' : 'var(--border-hair)'),
      transition: 'var(--transition-control)'
    }
  }, rest), color ? /*#__PURE__*/React.createElement("span", {
    style: {
      width: 6,
      height: 6,
      borderRadius: 'var(--radius-full)',
      background: color
    }
  }) : null, children, onRemove ? /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-label": "Remove",
    onClick: onRemove,
    style: {
      background: 'none',
      border: 0,
      padding: 0,
      marginLeft: 2,
      cursor: 'pointer',
      color: 'var(--text-faint)',
      fontFamily: 'var(--font-mono)',
      fontSize: 12,
      lineHeight: 1
    }
  }, "\xD7") : null);
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Tag.jsx", error: String((e && e.message) || e) }); }

// components/core/Tooltip.jsx
try { (() => {
/** Hover explanation. One line, no title, no rich content. */
function Tooltip({
  content,
  placement = 'top',
  children
}) {
  const [open, setOpen] = React.useState(false);
  const pos = placement === 'bottom' ? {
    top: 'calc(100% + 6px)',
    left: '50%',
    transform: 'translateX(-50%)'
  } : {
    bottom: 'calc(100% + 6px)',
    left: '50%',
    transform: 'translateX(-50%)'
  };
  return /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'relative',
      display: 'inline-flex'
    },
    onMouseEnter: () => setOpen(true),
    onMouseLeave: () => setOpen(false),
    onFocus: () => setOpen(true),
    onBlur: () => setOpen(false)
  }, children, /*#__PURE__*/React.createElement("span", {
    role: "tooltip",
    style: {
      position: 'absolute',
      ...pos,
      zIndex: 40,
      pointerEvents: 'none',
      opacity: open ? 1 : 0,
      transition: 'opacity var(--dur-fast) var(--ease-standard)',
      background: 'var(--surface-raised)',
      color: 'var(--text-primary)',
      border: '1px solid var(--border-line)',
      borderRadius: 'var(--radius-sm)',
      boxShadow: 'var(--shadow-2)',
      padding: 'var(--space-2) var(--space-4)',
      fontFamily: 'var(--font-ui)',
      fontSize: 'var(--size-xs)',
      whiteSpace: 'nowrap'
    }
  }, content));
}
Object.assign(__ds_scope, { Tooltip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Tooltip.jsx", error: String((e && e.message) || e) }); }

// components/data/DataTable.jsx
try { (() => {
/** Dense hairline table. Numeric columns are mono and right-aligned. */
function DataTable({
  columns = [],
  rows = [],
  selectedId,
  onSelectRow,
  rowKey = 'id',
  empty = 'No rows in this window.'
}) {
  const [hover, setHover] = React.useState(null);
  const cell = c => ({
    padding: 'var(--space-4)',
    textAlign: c.align || 'left',
    fontFamily: c.mono ? 'var(--font-mono)' : 'var(--font-ui)',
    fontSize: 'var(--size-sm)',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis'
  });
  if (!rows.length) return /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-9)',
      textAlign: 'center',
      color: 'var(--text-faint)',
      fontSize: 'var(--size-sm)'
    }
  }, empty);
  return /*#__PURE__*/React.createElement("table", {
    style: {
      width: '100%',
      borderCollapse: 'collapse',
      tableLayout: 'fixed'
    }
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, columns.map(c => /*#__PURE__*/React.createElement("th", {
    key: c.key,
    style: {
      ...cell(c),
      font: 'var(--text-label)',
      letterSpacing: 'var(--track-label)',
      textTransform: 'uppercase',
      color: 'var(--text-muted)',
      fontWeight: 'var(--weight-medium)',
      borderBottom: '1px solid var(--border-line)',
      width: c.width
    }
  }, c.label)))), /*#__PURE__*/React.createElement("tbody", null, rows.map(r => {
    const id = r[rowKey],
      sel = id != null && id === selectedId;
    return /*#__PURE__*/React.createElement("tr", {
      key: id,
      onClick: () => onSelectRow && onSelectRow(id),
      onMouseEnter: () => setHover(id),
      onMouseLeave: () => setHover(null),
      style: {
        cursor: onSelectRow ? 'pointer' : 'default',
        background: sel ? 'var(--surface-selected)' : hover === id ? 'var(--surface-hover)' : 'transparent',
        boxShadow: sel ? 'inset 2px 0 0 var(--magenta-3)' : 'none',
        transition: 'background-color var(--dur-fast) var(--ease-standard)'
      }
    }, columns.map(c => /*#__PURE__*/React.createElement("td", {
      key: c.key,
      style: {
        ...cell(c),
        color: c.muted ? 'var(--text-muted)' : 'var(--text-body)',
        borderBottom: '1px solid var(--border-hair)'
      }
    }, c.render ? c.render(r) : r[c.key])));
  })));
}
Object.assign(__ds_scope, { DataTable });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/DataTable.jsx", error: String((e && e.message) || e) }); }

// components/data/Meter.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const TONES = {
  accent: 'var(--magenta-3)',
  nominal: 'var(--aqua-3)',
  caution: 'var(--amber-3)',
  fault: 'var(--coral-3)'
};

/** Linear progress / utilisation bar. Square ends, hairline track. */
function Meter({
  value = 0,
  max = 100,
  label,
  valueLabel,
  tone = 'accent',
  height = 4,
  ...rest
}) {
  const pct = Math.max(0, Math.min(100, value / max * 100));
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      minWidth: 0
    }
  }, rest), label || valueLabel ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      gap: 'var(--space-4)',
      marginBottom: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-label)',
      letterSpacing: 'var(--track-label)',
      textTransform: 'uppercase',
      color: 'var(--text-muted)'
    }
  }, label), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--size-xs)',
      color: 'var(--text-body)'
    }
  }, valueLabel)) : null, /*#__PURE__*/React.createElement("div", {
    role: "progressbar",
    "aria-valuenow": value,
    "aria-valuemax": max,
    style: {
      height,
      background: 'var(--surface-inset)',
      border: '1px solid var(--border-hair)',
      borderRadius: 'var(--radius-xs)',
      overflow: 'hidden'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: pct + '%',
      height: '100%',
      background: TONES[tone],
      transition: 'width var(--dur-base) var(--ease-standard)'
    }
  })));
}
Object.assign(__ds_scope, { Meter });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/Meter.jsx", error: String((e && e.message) || e) }); }

// components/data/Readout.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Labelled instrument value. Mono, light weight, unit always attached. */
function Readout({
  label,
  value,
  unit,
  tone,
  delta,
  align = 'left',
  size = 'md',
  ...rest
}) {
  const fs = size === 'lg' ? 'var(--size-2xl)' : size === 'sm' ? 'var(--size-md)' : 'var(--size-xl)';
  const color = tone ? {
    nominal: 'var(--aqua-2)',
    caution: 'var(--amber-2)',
    fault: 'var(--coral-2)',
    accent: 'var(--magenta-2)'
  }[tone] : 'var(--text-primary)';
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      textAlign: align,
      minWidth: 0
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-label)',
      letterSpacing: 'var(--track-label)',
      textTransform: 'uppercase',
      color: 'var(--text-muted)',
      marginBottom: 'var(--space-3)'
    }
  }, label), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 'var(--space-2)',
      justifyContent: align === 'right' ? 'flex-end' : 'flex-start'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontWeight: 'var(--weight-light)',
      fontSize: fs,
      lineHeight: 1.1,
      color,
      letterSpacing: '-0.01em'
    }
  }, value), unit ? /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--size-sm)',
      color: 'var(--text-faint)'
    }
  }, unit) : null), delta ? /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 'var(--space-2)',
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--size-xs)',
      color: 'var(--text-muted)'
    }
  }, delta) : null);
}
Object.assign(__ds_scope, { Readout });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/Readout.jsx", error: String((e && e.message) || e) }); }

// components/data/StarIcon.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const SPRITE_URL = '/assets/icons/stellar-icons-modernist.svg';
const SPECTRAL_COLORS = {
  O: 'var(--spectral-o)',
  B: 'var(--spectral-b)',
  A: 'var(--spectral-a)',
  F: 'var(--spectral-f)',
  G: 'var(--spectral-g)',
  K: 'var(--spectral-k)',
  M: 'var(--spectral-m)',
  L: 'var(--spectral-l)',
  T: 'var(--spectral-t)',
  Y: 'var(--spectral-y)'
};
const CORES = ['hyper', 'super', 'bgiant', 'giant', 'subgiant', 'ms', 'dwarf', 'wd', 'browndwarf', 'proto', 'ns', 'bh'];
const MODIFIERS = ['companion', 'companion2', 'contact', 'variable', 'planets', 'accretion', 'jets', 'beams', 'magnetic', 'flare', 'nebulosity'];

/**
 * Composes layers from the stellar sprite in the correct z-order:
 * reference grid → luminosity arc → core → modifiers → class letter → size ticks.
 */
function StarIcon({
  core = 'ms',
  spectral = 'G',
  luminosity,
  modifiers = [],
  showClass = true,
  refGrid = false,
  size = 32,
  sprite = SPRITE_URL,
  title,
  ...rest
}) {
  const href = id => sprite + '#mo-' + id;
  return /*#__PURE__*/React.createElement("svg", _extends({
    width: size,
    height: size,
    viewBox: "0 0 64 64",
    role: "img",
    "aria-label": title || spectral + ' ' + core,
    style: {
      '--sp': SPECTRAL_COLORS[spectral] || 'var(--spectral-g)',
      '--ink': 'var(--ink-2)',
      '--bg': 'var(--void-0)',
      display: 'block',
      overflow: 'visible'
    }
  }, rest), title ? /*#__PURE__*/React.createElement("title", null, title) : null, refGrid ? /*#__PURE__*/React.createElement("use", {
    href: href('ref-grid')
  }) : null, luminosity ? /*#__PURE__*/React.createElement("use", {
    href: href('lum-' + luminosity)
  }) : null, /*#__PURE__*/React.createElement("use", {
    href: href('core-' + core)
  }), modifiers.map(m => /*#__PURE__*/React.createElement("use", {
    key: m,
    href: href('mod-' + m)
  })), showClass ? /*#__PURE__*/React.createElement("use", {
    href: href('cls-' + spectral)
  }) : null);
}
Object.assign(__ds_scope, { SPRITE_URL, SPECTRAL_COLORS, CORES, MODIFIERS, StarIcon });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/StarIcon.jsx", error: String((e && e.message) || e) }); }

// components/data/StatusDot.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const TONES = {
  nominal: 'var(--status-nominal)',
  caution: 'var(--status-caution)',
  fault: 'var(--status-fault)',
  archive: 'var(--status-archive)',
  idle: 'var(--ink-4)'
};

/** 8px status dot with optional label. The only round element besides Switch. */
function StatusDot({
  tone = 'idle',
  label,
  pulse = false,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 'var(--space-3)'
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    style: {
      width: 8,
      height: 8,
      borderRadius: 'var(--radius-full)',
      background: TONES[tone],
      boxShadow: pulse && tone === 'nominal' ? 'var(--glow-nominal)' : 'none',
      flex: '0 0 8px'
    }
  }), label ? /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-label)',
      letterSpacing: 'var(--track-label)',
      textTransform: 'uppercase',
      color: 'var(--text-muted)'
    }
  }, label) : null);
}
Object.assign(__ds_scope, { StatusDot });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/StatusDot.jsx", error: String((e && e.message) || e) }); }

// components/forms/Checkbox.jsx
try { (() => {
/** Square checkbox. Checked state is magenta with a knockout tick. */
function Checkbox({
  label,
  description,
  checked = false,
  indeterminate = false,
  disabled,
  onChange
}) {
  const on = checked || indeterminate;
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'flex',
      gap: 'var(--space-4)',
      alignItems: 'flex-start',
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.4 : 1
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 16,
      height: 16,
      flex: '0 0 16px',
      marginTop: 1,
      display: 'grid',
      placeItems: 'center',
      background: on ? 'var(--magenta-3)' : 'var(--surface-inset)',
      border: '1px solid ' + (on ? 'var(--magenta-3)' : 'var(--border-line)'),
      borderRadius: 'var(--radius-xs)',
      transition: 'var(--transition-control)'
    }
  }, indeterminate ? /*#__PURE__*/React.createElement("span", {
    style: {
      width: 8,
      height: 2,
      background: 'var(--void-0)'
    }
  }) : checked ? /*#__PURE__*/React.createElement("svg", {
    width: "10",
    height: "10",
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "var(--void-0)",
    strokeWidth: "3.5",
    strokeLinecap: "round",
    "aria-hidden": "true"
  }, /*#__PURE__*/React.createElement("path", {
    d: "M5 13l4 4L19 7"
  })) : null, /*#__PURE__*/React.createElement("input", {
    type: "checkbox",
    checked: checked,
    disabled: disabled,
    onChange: e => onChange && onChange(e.target.checked),
    style: {
      position: 'absolute',
      opacity: 0,
      width: 0,
      height: 0
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--size-sm)',
      color: 'var(--text-primary)'
    }
  }, label), description ? /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      fontSize: 'var(--size-xs)',
      color: 'var(--text-faint)',
      marginTop: 2
    }
  }, description) : null));
}
Object.assign(__ds_scope, { Checkbox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Checkbox.jsx", error: String((e && e.message) || e) }); }

// components/forms/Input.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const H = {
  sm: 'var(--control-sm)',
  md: 'var(--control-md)',
  lg: 'var(--control-lg)'
};

/** Text field. Mono when it holds instrument values or query syntax. */
function Input({
  label,
  hint,
  error,
  size = 'md',
  mono = false,
  prefix,
  suffix,
  disabled,
  ...rest
}) {
  const [focus, setFocus] = React.useState(false);
  const border = error ? 'var(--coral-4)' : focus ? 'var(--border-focus)' : 'var(--border-line)';
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'block',
      opacity: disabled ? 0.4 : 1
    }
  }, label ? /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-label)',
      letterSpacing: 'var(--track-label)',
      textTransform: 'uppercase',
      color: 'var(--text-muted)',
      marginBottom: 'var(--space-3)'
    }
  }, label) : null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-3)',
      height: H[size],
      padding: '0 var(--space-4)',
      background: 'var(--surface-inset)',
      border: '1px solid ' + border,
      borderRadius: 'var(--radius-sm)',
      boxShadow: focus ? 'var(--shadow-focus)' : 'none',
      transition: 'var(--transition-control)'
    }
  }, prefix ? /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-faint)',
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--size-xs)'
    }
  }, prefix) : null, /*#__PURE__*/React.createElement("input", _extends({
    disabled: disabled,
    onFocus: () => setFocus(true),
    onBlur: () => setFocus(false),
    style: {
      flex: 1,
      minWidth: 0,
      background: 'none',
      border: 0,
      outline: 'none',
      padding: 0,
      color: 'var(--text-primary)',
      fontFamily: mono ? 'var(--font-mono)' : 'var(--font-ui)',
      fontSize: 'var(--size-sm)'
    }
  }, rest)), suffix ? /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-faint)',
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--size-xs)'
    }
  }, suffix) : null), error || hint ? /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 'var(--space-2)',
      fontSize: 'var(--size-xs)',
      color: error ? 'var(--coral-2)' : 'var(--text-faint)'
    }
  }, error || hint) : null);
}
Object.assign(__ds_scope, { Input });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Input.jsx", error: String((e && e.message) || e) }); }

// components/forms/Select.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Native select styled as a Galaxy control. */
function Select({
  label,
  options = [],
  hint,
  size = 'md',
  disabled,
  ...rest
}) {
  const [focus, setFocus] = React.useState(false);
  const H = {
    sm: 'var(--control-sm)',
    md: 'var(--control-md)',
    lg: 'var(--control-lg)'
  };
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'block',
      opacity: disabled ? 0.4 : 1
    }
  }, label ? /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-label)',
      letterSpacing: 'var(--track-label)',
      textTransform: 'uppercase',
      color: 'var(--text-muted)',
      marginBottom: 'var(--space-3)'
    }
  }, label) : null, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("select", _extends({
    disabled: disabled,
    onFocus: () => setFocus(true),
    onBlur: () => setFocus(false),
    style: {
      width: '100%',
      height: H[size],
      appearance: 'none',
      padding: '0 var(--space-8) 0 var(--space-4)',
      background: 'var(--surface-inset)',
      color: 'var(--text-primary)',
      fontFamily: 'var(--font-ui)',
      fontSize: 'var(--size-sm)',
      border: '1px solid ' + (focus ? 'var(--border-focus)' : 'var(--border-line)'),
      borderRadius: 'var(--radius-sm)',
      outline: 'none',
      boxShadow: focus ? 'var(--shadow-focus)' : 'none',
      transition: 'var(--transition-control)'
    }
  }, rest), options.map(o => {
    const v = typeof o === 'string' ? o : o.value,
      l = typeof o === 'string' ? o : o.label;
    return /*#__PURE__*/React.createElement("option", {
      key: v,
      value: v
    }, l);
  })), /*#__PURE__*/React.createElement("svg", {
    width: "10",
    height: "10",
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "2",
    strokeLinecap: "round",
    "aria-hidden": "true",
    style: {
      position: 'absolute',
      right: 'var(--space-4)',
      top: '50%',
      marginTop: -5,
      color: 'var(--text-faint)',
      pointerEvents: 'none'
    }
  }, /*#__PURE__*/React.createElement("path", {
    d: "M6 9l6 6 6-6"
  }))), hint ? /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 'var(--space-2)',
      fontSize: 'var(--size-xs)',
      color: 'var(--text-faint)'
    }
  }, hint) : null);
}
Object.assign(__ds_scope, { Select });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Select.jsx", error: String((e && e.message) || e) }); }

// components/forms/Switch.jsx
try { (() => {
/** Switch for live, immediately-applied state (telemetry on/off, overlays). */
function Switch({
  label,
  checked = false,
  disabled,
  onChange
}) {
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 'var(--space-4)',
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.4 : 1
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 30,
      height: 16,
      flex: '0 0 30px',
      padding: 2,
      display: 'flex',
      alignItems: 'center',
      justifyContent: checked ? 'flex-end' : 'flex-start',
      background: checked ? 'var(--magenta-4)' : 'var(--surface-inset)',
      border: '1px solid ' + (checked ? 'var(--magenta-3)' : 'var(--border-line)'),
      borderRadius: 'var(--radius-full)',
      transition: 'var(--transition-control)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 10,
      height: 10,
      borderRadius: 'var(--radius-full)',
      background: checked ? 'var(--magenta-1)' : 'var(--ink-4)',
      transition: 'background-color var(--dur-fast) var(--ease-standard)'
    }
  }), /*#__PURE__*/React.createElement("input", {
    type: "checkbox",
    checked: checked,
    disabled: disabled,
    onChange: e => onChange && onChange(e.target.checked),
    style: {
      position: 'absolute',
      opacity: 0,
      width: 0,
      height: 0
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--size-sm)',
      color: 'var(--text-primary)'
    }
  }, label));
}
Object.assign(__ds_scope, { Switch });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Switch.jsx", error: String((e && e.message) || e) }); }

// ui_kits/atlas/AtlasShell.jsx
try { (() => {
const {
  IconButton,
  Badge,
  StatusDot,
  Tag,
  Dialog,
  Button,
  Input,
  Select,
  Checkbox
} = window.GalaxyDesignSystem_658871;
const LUCIDE = 'https://unpkg.com/lucide-static@0.544.0/icons/';
const Glyph = ({
  name,
  size = 16,
  dim
}) => /*#__PURE__*/React.createElement("img", {
  src: LUCIDE + name + '.svg',
  width: size,
  height: size,
  alt: "",
  style: {
    opacity: dim ? 0.55 : 0.9,
    filter: 'invert(92%) sepia(8%) saturate(400%) hue-rotate(190deg)'
  }
});
const NAV = [{
  k: 'catalog',
  icon: 'table-2',
  label: 'Catalogue'
}, {
  k: 'object',
  icon: 'orbit',
  label: 'Object'
}, {
  k: 'survey',
  icon: 'calendar-clock',
  label: 'Survey planner'
}];
function Rail({
  view,
  setView
}) {
  return /*#__PURE__*/React.createElement("nav", {
    style: {
      width: 'var(--rail-width)',
      flex: '0 0 var(--rail-width)',
      background: 'var(--void-0)',
      borderRight: '1px solid var(--border-hair)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: 'var(--space-4) 0',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-display)',
      fontWeight: 300,
      fontSize: 20,
      letterSpacing: '-0.05em',
      color: 'var(--ink-1)',
      marginBottom: 'var(--space-3)'
    }
  }, "G"), NAV.map(n => /*#__PURE__*/React.createElement(IconButton, {
    key: n.k,
    label: n.label,
    selected: view === n.k,
    onClick: () => setView(n.k)
  }, /*#__PURE__*/React.createElement(Glyph, {
    name: n.icon
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement(IconButton, {
    label: "Settings"
  }, /*#__PURE__*/React.createElement(Glyph, {
    name: "settings",
    dim: true
  })));
}
function TopBar({
  title,
  crumb,
  onPlan
}) {
  return /*#__PURE__*/React.createElement("header", {
    style: {
      height: 'var(--topbar-height)',
      flex: '0 0 var(--topbar-height)',
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-5)',
      padding: '0 var(--space-5)',
      background: 'var(--void-1)',
      borderBottom: '1px solid var(--border-hair)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "gx-label"
  }, crumb), /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-faint)'
    }
  }, "/"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--size-sm)',
      color: 'var(--text-primary)',
      fontWeight: 'var(--weight-medium)'
    }
  }, title), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement(StatusDot, {
    tone: "nominal",
    label: "Ingest live",
    pulse: true
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--text-data)',
      color: 'var(--text-muted)'
    }
  }, "04:12:07 UTC"), /*#__PURE__*/React.createElement(Button, {
    size: "sm",
    variant: "primary",
    onClick: onPlan
  }, "Queue survey"));
}
function AtlasShell() {
  const [view, setView] = React.useState('catalog');
  const [selected, setSelected] = React.useState('HD37022');
  const [planOpen, setPlanOpen] = React.useState(false);
  const [queued, setQueued] = React.useState(false);
  const obj = OBJECTS.find(o => o.id === selected) || OBJECTS[0];
  const open = id => {
    setSelected(id);
    setView('object');
  };
  const titles = {
    catalog: 'Catalogue',
    object: obj.name,
    survey: 'Survey planner'
  };
  const crumbs = {
    catalog: 'FIELD F-07',
    object: 'OBJECT',
    survey: 'SCHEDULER'
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      height: '100vh',
      background: 'var(--bg-app)',
      fontFamily: 'var(--font-ui)',
      color: 'var(--text-body)'
    }
  }, /*#__PURE__*/React.createElement(Rail, {
    view: view,
    setView: setView
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 0,
      display: 'flex',
      flexDirection: 'column'
    }
  }, /*#__PURE__*/React.createElement(TopBar, {
    title: titles[view],
    crumb: crumbs[view],
    onPlan: () => setPlanOpen(true)
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minHeight: 0,
      display: 'flex'
    }
  }, view === 'catalog' ? /*#__PURE__*/React.createElement(CatalogScreen, {
    selected: selected,
    onSelect: setSelected,
    onOpen: open
  }) : null, view === 'object' ? /*#__PURE__*/React.createElement(ObjectScreen, {
    obj: obj,
    onBack: () => setView('catalog')
  }) : null, view === 'survey' ? /*#__PURE__*/React.createElement(SurveyScreen, {
    queued: queued,
    onPlan: () => setPlanOpen(true)
  }) : null)), /*#__PURE__*/React.createElement(Dialog, {
    open: planOpen,
    label: "Survey planner",
    title: "Queue deep field 07",
    onClose: () => setPlanOpen(false),
    footer: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Button, {
      variant: "ghost",
      onClick: () => setPlanOpen(false)
    }, "Cancel"), /*#__PURE__*/React.createElement(Button, {
      variant: "primary",
      onClick: () => {
        setQueued(true);
        setPlanOpen(false);
        setView('survey');
      }
    }, "Queue survey"))
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement(Select, {
    label: "Field",
    options: FIELDS.map(f => ({
      value: f.id,
      label: f.id + ' · ' + f.name
    })),
    defaultValue: "F-07"
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Frames",
    mono: true,
    defaultValue: "12"
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Exposure",
    mono: true,
    suffix: "s",
    defaultValue: "1200"
  }), /*#__PURE__*/React.createElement(Select, {
    label: "Band",
    options: ['g′', 'r′', 'i′', 'z′'],
    defaultValue: "r\u2032"
  })), /*#__PURE__*/React.createElement(Checkbox, {
    label: "Defer if seeing exceeds 1.2\u2033",
    description: "The scheduler will hold the block rather than degrade the set."
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 'var(--size-sm)',
      color: 'var(--text-muted)'
    }
  }, "Twelve frames at 1,200 s. Estimated completion 06:40 UTC."))));
}
Object.assign(window, {
  AtlasShell,
  Glyph,
  LUCIDE
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/atlas/AtlasShell.jsx", error: String((e && e.message) || e) }); }

// ui_kits/atlas/CatalogScreen.jsx
try { (() => {
const {
  Card,
  DataTable,
  StarIcon,
  StatusDot,
  Badge,
  Tag,
  Input,
  Select,
  Checkbox,
  Button,
  Readout,
  Meter,
  Tabs
} = window.GalaxyDesignSystem_658871;
function FieldList({}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column'
    }
  }, FIELDS.map(f => /*#__PURE__*/React.createElement("button", {
    key: f.id,
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-3)',
      background: f.id === 'F-07' ? 'var(--surface-selected)' : 'transparent',
      border: 0,
      boxShadow: f.id === 'F-07' ? 'inset 2px 0 0 var(--magenta-3)' : 'none',
      padding: 'var(--space-3) var(--space-5)',
      cursor: 'pointer',
      textAlign: 'left',
      fontFamily: 'var(--font-ui)',
      fontSize: 'var(--size-sm)',
      color: f.id === 'F-07' ? 'var(--text-primary)' : 'var(--text-body)'
    }
  }, /*#__PURE__*/React.createElement(StatusDot, {
    tone: f.status
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--size-xs)',
      color: 'var(--text-muted)',
      width: 36
    }
  }, f.id), /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1,
      minWidth: 0,
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, f.name), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--size-xs)',
      color: 'var(--text-faint)'
    }
  }, f.objects.toLocaleString()))));
}
function CatalogScreen({
  selected,
  onSelect,
  onOpen
}) {
  const [tab, setTab] = React.useState('objects');
  const obj = OBJECTS.find(o => o.id === selected) || OBJECTS[0];
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("aside", {
    style: {
      width: 'var(--sidebar-width)',
      flex: '0 0 var(--sidebar-width)',
      background: 'var(--void-1)',
      borderRight: '1px solid var(--border-hair)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'auto'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-5)',
      display: 'grid',
      gap: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement(Input, {
    label: "Search catalogue",
    placeholder: "Object, designation, coords"
  }), /*#__PURE__*/React.createElement(Select, {
    label: "Spectral class",
    options: ['All classes', 'O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'T', 'Y']
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Limiting mag",
    mono: true,
    suffix: "mag",
    defaultValue: "21.5"
  }), /*#__PURE__*/React.createElement(Checkbox, {
    label: "Include archived",
    description: "512 additional objects."
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '0 var(--space-5) var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "gx-label"
  }, "FIELDS")), /*#__PURE__*/React.createElement(FieldList, null)), /*#__PURE__*/React.createElement("main", {
    style: {
      flex: 1,
      minWidth: 0,
      overflow: 'auto',
      padding: 'var(--space-5)',
      display: 'grid',
      gap: 'var(--space-5)',
      alignContent: 'start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4,1fr)',
      gap: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement(Readout, {
    label: "Objects",
    value: "1,847"
  })), /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement(Readout, {
    label: "Seeing",
    value: "0.42",
    unit: "\u2033",
    tone: "nominal"
  })), /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement(Readout, {
    label: "Zero point",
    value: "\u221226.74",
    unit: "mag",
    delta: "\u22120.03 since 04:12 UTC"
  })), /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement(Meter, {
    label: "Ingest",
    valueLabel: "4 of 12 frames",
    value: 4,
    max: 12
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement(StatusDot, {
    tone: "caution",
    label: "2 detectors degraded"
  })))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-4)',
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement(Tag, {
    onRemove: () => {}
  }, "field:F-07"), /*#__PURE__*/React.createElement(Tag, {
    onRemove: () => {}
  }, "mag < 21.5"), /*#__PURE__*/React.createElement(Tag, {
    color: "var(--spectral-o)",
    onRemove: () => {}
  }, "class:O,B"), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement(Button, {
    size: "sm",
    variant: "secondary"
  }, "Export CSV")), /*#__PURE__*/React.createElement(Card, {
    padding: 0
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-4) var(--space-5) 0'
    }
  }, /*#__PURE__*/React.createElement(Tabs, {
    value: tab,
    onChange: setTab,
    items: [{
      value: 'objects',
      label: 'Objects',
      count: 1847
    }, {
      value: 'frames',
      label: 'Frames',
      count: 96
    }, {
      value: 'log',
      label: 'Ingest log'
    }]
  })), tab === 'objects' ? /*#__PURE__*/React.createElement(DataTable, {
    rows: OBJECTS,
    selectedId: selected,
    onSelectRow: onSelect,
    columns: [{
      key: 'glyph',
      label: '',
      width: 52,
      render: r => /*#__PURE__*/React.createElement(StarIcon, {
        sprite: SPRITE,
        spectral: r.spectral,
        core: r.core,
        luminosity: r.lum,
        modifiers: r.mods,
        showClass: false,
        size: 22
      })
    }, {
      key: 'name',
      label: 'Object',
      render: r => /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("span", {
        style: {
          color: 'var(--text-primary)'
        }
      }, r.name), /*#__PURE__*/React.createElement("span", {
        style: {
          color: 'var(--text-faint)',
          marginLeft: 8,
          fontSize: 'var(--size-xs)'
        }
      }, r.alt))
    }, {
      key: 'cls',
      label: 'Class',
      mono: true,
      width: 100
    }, {
      key: 'mag',
      label: 'Mag V',
      mono: true,
      align: 'right',
      width: 88
    }, {
      key: 'ra',
      label: 'RA',
      mono: true,
      width: 132,
      muted: true
    }, {
      key: 'dec',
      label: 'Dec',
      mono: true,
      width: 124,
      muted: true
    }, {
      key: 'dist',
      label: 'Distance',
      mono: true,
      align: 'right',
      width: 96
    }, {
      key: 'status',
      label: 'Status',
      width: 120,
      render: r => /*#__PURE__*/React.createElement(StatusDot, {
        tone: r.status,
        label: r.status
      })
    }]
  }) : tab === 'frames' ? /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-9)',
      textAlign: 'center',
      color: 'var(--text-faint)',
      fontSize: 'var(--size-sm)'
    }
  }, "Frame browser is not part of this recreation \u2014 no source view was supplied.") : /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-5)',
      display: 'grid',
      gap: 'var(--space-3)',
      font: 'var(--text-data)',
      color: 'var(--text-body)'
    }
  }, [['04:12:07', 'Ingest F-07 frame 4 of 12 complete', 'nominal'], ['03:51:44', 'Detector 2 gain degraded to 0.93', 'caution'], ['22:18:02', 'Field F-04 lost sync mid-egress', 'fault'], ['21:40:19', 'Astrometric solution 0.9 mas', 'nominal']].map(([t, m, s], i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      display: 'flex',
      gap: 'var(--space-5)',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-faint)'
    }
  }, t), /*#__PURE__*/React.createElement(StatusDot, {
    tone: s
  }), /*#__PURE__*/React.createElement("span", null, m)))))), /*#__PURE__*/React.createElement("aside", {
    style: {
      width: 'var(--inspector-width)',
      flex: '0 0 var(--inspector-width)',
      background: 'var(--void-1)',
      borderLeft: '1px solid var(--border-hair)',
      overflow: 'auto',
      padding: 'var(--space-5)',
      display: 'grid',
      gap: 'var(--space-5)',
      alignContent: 'start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-5)',
      alignItems: 'flex-start'
    }
  }, /*#__PURE__*/React.createElement(StarIcon, {
    sprite: SPRITE,
    spectral: obj.spectral,
    core: obj.core,
    luminosity: obj.lum,
    modifiers: obj.mods,
    refGrid: true,
    size: 64
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-h3)',
      color: 'var(--text-primary)'
    }
  }, obj.name), /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-data)',
      color: 'var(--text-muted)',
      marginTop: 2
    }
  }, obj.alt), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement(Badge, {
    tone: obj.status
  }, obj.status)))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement(Readout, {
    label: "Class",
    value: obj.cls,
    size: "sm"
  }), /*#__PURE__*/React.createElement(Readout, {
    label: "Mag V",
    value: obj.mag,
    size: "sm"
  }), /*#__PURE__*/React.createElement(Readout, {
    label: "T eff",
    value: obj.teff,
    unit: "K",
    size: "sm"
  }), /*#__PURE__*/React.createElement(Readout, {
    label: "Radius",
    value: obj.radius,
    unit: "R\u2609",
    size: "sm"
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-3)',
      font: 'var(--text-data)'
    }
  }, [['RA', obj.ra], ['DEC', obj.dec], ['DISTANCE', obj.dist], ['FIELD', obj.field]].map(([k, v]) => /*#__PURE__*/React.createElement("div", {
    key: k,
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      gap: 'var(--space-4)',
      paddingBottom: 'var(--space-3)',
      borderBottom: '1px solid var(--border-hair)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "gx-label"
  }, k), /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-primary)'
    }
  }, v)))), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 'var(--size-sm)',
      color: 'var(--text-body)'
    }
  }, obj.notes), /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    fullWidth: true,
    onClick: () => onOpen(obj.id)
  }, "Open object")));
}
Object.assign(window, {
  CatalogScreen,
  FieldList
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/atlas/CatalogScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/atlas/ObjectScreen.jsx
try { (() => {
const {
  Card,
  Button,
  Badge,
  Tag,
  Readout,
  Meter,
  StatusDot,
  StarIcon,
  DataTable,
  Tabs,
  Tooltip
} = window.GalaxyDesignSystem_658871;
function ObjectScreen({
  obj,
  onBack
}) {
  const [tab, setTab] = React.useState('overview');
  return /*#__PURE__*/React.createElement("main", {
    style: {
      flex: 1,
      minWidth: 0,
      overflow: 'auto'
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "gx-field",
    style: {
      position: 'relative',
      padding: 'var(--space-8) var(--space-8) var(--space-7)',
      borderBottom: '1px solid var(--border-hair)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      inset: 0,
      background: 'var(--scrim-bottom)'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      display: 'flex',
      gap: 'var(--space-8)',
      alignItems: 'flex-end'
    }
  }, /*#__PURE__*/React.createElement(StarIcon, {
    sprite: SPRITE,
    spectral: obj.spectral,
    core: obj.core,
    luminosity: obj.lum,
    modifiers: obj.mods,
    refGrid: true,
    size: 120
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "gx-label"
  }, obj.field, " \xB7 SPECTRAL CLASS ", obj.cls), /*#__PURE__*/React.createElement("h1", {
    style: {
      fontWeight: 300,
      fontSize: 'var(--size-3xl)',
      letterSpacing: 'var(--track-display)',
      lineHeight: 1.05,
      margin: 'var(--space-3) 0 var(--space-2)'
    }
  }, obj.name), /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--text-data)',
      color: 'var(--text-muted)'
    }
  }, obj.alt, " \xB7 ", obj.ra, " \xB7 ", obj.dec)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-3)',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Badge, {
    tone: obj.status
  }, obj.status), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    size: "sm",
    onClick: onBack
  }, "Back to catalogue"), /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    size: "sm"
  }, "Queue follow-up")))), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-5) var(--space-8) 0'
    }
  }, /*#__PURE__*/React.createElement(Tabs, {
    value: tab,
    onChange: setTab,
    items: [{
      value: 'overview',
      label: 'Overview'
    }, {
      value: 'photometry',
      label: 'Photometry',
      count: 96
    }, {
      value: 'history',
      label: 'Observation history',
      count: 31
    }]
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-5) var(--space-8) var(--space-8)',
      display: 'grid',
      gridTemplateColumns: '2fr 1fr',
      gap: 'var(--space-5)',
      alignItems: 'start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement(Card, {
    label: "Derived parameters",
    title: "Physical properties"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4,1fr)',
      gap: 'var(--space-7)'
    }
  }, /*#__PURE__*/React.createElement(Readout, {
    label: "T eff",
    value: obj.teff,
    unit: "K"
  }), /*#__PURE__*/React.createElement(Readout, {
    label: "Radius",
    value: obj.radius,
    unit: "R\u2609"
  }), /*#__PURE__*/React.createElement(Readout, {
    label: "Mag V",
    value: obj.mag
  }), /*#__PURE__*/React.createElement(Readout, {
    label: "Distance",
    value: obj.dist.split(' ')[0],
    unit: obj.dist.split(' ')[1]
  }))), /*#__PURE__*/React.createElement(Card, {
    label: "Light curve",
    title: "Photometric series"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      height: 150,
      display: 'grid',
      placeItems: 'center',
      background: 'var(--surface-inset)',
      border: '1px dashed var(--border-line)',
      borderRadius: 'var(--radius-sm)',
      textAlign: 'center',
      padding: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--size-sm)',
      color: 'var(--text-faint)',
      maxWidth: 420
    }
  }, "Chart intentionally blank \u2014 no charting library or plot design was supplied with the source material."))), /*#__PURE__*/React.createElement(Card, {
    label: "Recent frames",
    title: "Observation history",
    padding: 0
  }, /*#__PURE__*/React.createElement(DataTable, {
    rowKey: "fid",
    rows: [{
      fid: '2026-089-04',
      band: 'r′',
      exp: '1200 s',
      seeing: '0.42',
      zp: '−26.74',
      st: 'nominal'
    }, {
      fid: '2026-089-03',
      band: 'r′',
      exp: '1200 s',
      seeing: '0.51',
      zp: '−26.71',
      st: 'nominal'
    }, {
      fid: '2026-089-02',
      band: 'g′',
      exp: '900 s',
      seeing: '0.88',
      zp: '−26.44',
      st: 'caution'
    }, {
      fid: '2026-088-11',
      band: 'i′',
      exp: '1200 s',
      seeing: '1.31',
      zp: '—',
      st: 'fault'
    }],
    columns: [{
      key: 'fid',
      label: 'Frame',
      mono: true
    }, {
      key: 'band',
      label: 'Band',
      mono: true,
      width: 70
    }, {
      key: 'exp',
      label: 'Exposure',
      mono: true,
      align: 'right',
      width: 96
    }, {
      key: 'seeing',
      label: 'Seeing ″',
      mono: true,
      align: 'right',
      width: 96
    }, {
      key: 'zp',
      label: 'Zero pt',
      mono: true,
      align: 'right',
      width: 96
    }, {
      key: 'st',
      label: 'Status',
      width: 120,
      render: r => /*#__PURE__*/React.createElement(StatusDot, {
        tone: r.st,
        label: r.st
      })
    }]
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement(Card, {
    label: "Classification",
    title: "Sprite composition"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-4)',
      font: 'var(--text-data)'
    }
  }, [['CORE', 'mo-core-' + obj.core], ['LUMINOSITY', 'mo-lum-' + obj.lum], ['CLASS LETTER', 'mo-cls-' + obj.spectral]].concat(obj.mods.map(m => ['MODIFIER', 'mo-mod-' + m])).map(([k, v], i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "gx-label"
  }, k), /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-primary)'
    }
  }, v))))), /*#__PURE__*/React.createElement(Card, {
    label: "Data quality",
    title: "Detector state"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement(Meter, {
    label: "Astrometric weight",
    valueLabel: "0.91",
    value: 91
  }), /*#__PURE__*/React.createElement(Meter, {
    label: "Photometric weight",
    valueLabel: "0.78",
    value: 78,
    tone: "caution"
  }), /*#__PURE__*/React.createElement(StatusDot, {
    tone: obj.status,
    label: obj.status === 'fault' ? 'Lost sync 22:18 UTC' : 'Within tolerance'
  }))), /*#__PURE__*/React.createElement(Card, {
    label: "Operator note",
    title: "Notes"
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 'var(--size-sm)'
    }
  }, obj.notes), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-3)',
      marginTop: 'var(--space-5)',
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement(Tag, {
    color: 'var(--spectral-' + obj.spectral.toLowerCase() + ')'
  }, obj.cls), obj.mods.map(m => /*#__PURE__*/React.createElement(Tag, {
    key: m
  }, m)))))));
}
Object.assign(window, {
  ObjectScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/atlas/ObjectScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/atlas/SurveyScreen.jsx
try { (() => {
const {
  Card,
  Button,
  Badge,
  Readout,
  Meter,
  StatusDot,
  DataTable,
  Switch,
  Select,
  Input,
  Checkbox
} = window.GalaxyDesignSystem_658871;
const STATE_TONE = {
  running: 'nominal',
  queued: 'idle',
  complete: 'archive',
  halted: 'fault'
};
function SurveyScreen({
  queued,
  onPlan
}) {
  const [live, setLive] = React.useState(true);
  const [grid, setGrid] = React.useState(false);
  const rows = queued ? [{
    id: 'Q-120',
    target: 'Deep field 07',
    frames: 12,
    done: 0,
    exp: '1200 s',
    eta: '06:40 UTC',
    state: 'queued'
  }, ...QUEUE] : QUEUE;
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("main", {
    style: {
      flex: 1,
      minWidth: 0,
      overflow: 'auto',
      padding: 'var(--space-5)',
      display: 'grid',
      gap: 'var(--space-5)',
      alignContent: 'start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4,1fr)',
      gap: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement(Readout, {
    label: "Blocks tonight",
    value: String(rows.length)
  })), /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement(Readout, {
    label: "On sky",
    value: "4.2",
    unit: "h",
    tone: "nominal"
  })), /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement(Readout, {
    label: "Lost to weather",
    value: "0.8",
    unit: "h",
    tone: "caution"
  })), /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement(Readout, {
    label: "Next block",
    value: "06:40",
    unit: "UTC"
  }))), /*#__PURE__*/React.createElement(Card, {
    label: "Scheduler",
    title: "Tonight's queue",
    padding: 0,
    actions: /*#__PURE__*/React.createElement(Button, {
      size: "sm",
      variant: "primary",
      onClick: onPlan
    }, "Queue survey")
  }, /*#__PURE__*/React.createElement(DataTable, {
    rows: rows,
    columns: [{
      key: 'id',
      label: 'Block',
      mono: true,
      width: 90
    }, {
      key: 'target',
      label: 'Target'
    }, {
      key: 'exp',
      label: 'Exposure',
      mono: true,
      align: 'right',
      width: 100
    }, {
      key: 'progress',
      label: 'Frames',
      width: 190,
      render: r => /*#__PURE__*/React.createElement(Meter, {
        value: r.done,
        max: r.frames,
        height: 2,
        tone: r.state === 'halted' ? 'fault' : 'accent',
        valueLabel: r.done + ' of ' + r.frames
      })
    }, {
      key: 'eta',
      label: 'ETA',
      mono: true,
      align: 'right',
      width: 100
    }, {
      key: 'state',
      label: 'State',
      width: 120,
      render: r => /*#__PURE__*/React.createElement(StatusDot, {
        tone: STATE_TONE[r.state],
        label: r.state
      })
    }]
  })), /*#__PURE__*/React.createElement(Card, {
    label: "Fields",
    title: "Field readiness",
    padding: 0
  }, /*#__PURE__*/React.createElement(DataTable, {
    rows: FIELDS,
    columns: [{
      key: 'id',
      label: 'Field',
      mono: true,
      width: 90
    }, {
      key: 'name',
      label: 'Name'
    }, {
      key: 'objects',
      label: 'Objects',
      mono: true,
      align: 'right',
      width: 110,
      render: r => r.objects.toLocaleString()
    }, {
      key: 'status',
      label: 'Status',
      width: 130,
      render: r => /*#__PURE__*/React.createElement(StatusDot, {
        tone: r.status,
        label: r.status
      })
    }]
  }))), /*#__PURE__*/React.createElement("aside", {
    style: {
      width: 'var(--inspector-width)',
      flex: '0 0 var(--inspector-width)',
      background: 'var(--void-1)',
      borderLeft: '1px solid var(--border-hair)',
      overflow: 'auto',
      padding: 'var(--space-5)',
      display: 'grid',
      gap: 'var(--space-5)',
      alignContent: 'start'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("span", {
    className: "gx-label"
  }, "CONDITIONS"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 'var(--space-5)',
      marginTop: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement(Readout, {
    label: "Seeing",
    value: "0.42",
    unit: "\u2033",
    tone: "nominal",
    size: "sm"
  }), /*#__PURE__*/React.createElement(Readout, {
    label: "Airmass",
    value: "1.08",
    size: "sm"
  }), /*#__PURE__*/React.createElement(Readout, {
    label: "Sky bright",
    value: "21.3",
    unit: "mag/\u25A1\u2033",
    size: "sm"
  }), /*#__PURE__*/React.createElement(Readout, {
    label: "Humidity",
    value: "38",
    unit: "%",
    size: "sm"
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "gx-label"
  }, "DISPLAY"), /*#__PURE__*/React.createElement(Switch, {
    label: "Live telemetry",
    checked: live,
    onChange: setLive
  }), /*#__PURE__*/React.createElement(Switch, {
    label: "Grid overlay",
    checked: grid,
    onChange: setGrid
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "gx-label"
  }, "NEW BLOCK"), /*#__PURE__*/React.createElement(Select, {
    label: "Field",
    options: FIELDS.map(f => f.id + ' · ' + f.name)
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Frames",
    mono: true,
    defaultValue: "12"
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Exposure",
    mono: true,
    suffix: "s",
    defaultValue: "1200"
  }), /*#__PURE__*/React.createElement(Checkbox, {
    label: "Defer if seeing exceeds 1.2\u2033"
  }), /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    fullWidth: true,
    onClick: onPlan
  }, "Review block"))));
}
Object.assign(window, {
  SurveyScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/atlas/SurveyScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/atlas/catalog-data.js
try { (() => {
// Sample catalogue. Values are plausible but illustrative — no real Galaxy data was supplied.
const SPRITE = '../../assets/icons/stellar-icons-modernist.svg';
const OBJECTS = [{
  id: 'HD37022',
  name: 'HD 37022',
  alt: 'θ¹ Ori C',
  cls: 'O6Vp',
  spectral: 'O',
  core: 'super',
  lum: 1,
  mods: ['companion'],
  mag: '+5.13',
  ra: '05h 35m 16.5s',
  dec: '−05° 23′ 23″',
  dist: '412 pc',
  status: 'nominal',
  field: 'F-07',
  teff: '39,000',
  radius: '10.6',
  notes: 'Dominant ionising source of the Trapezium. Strong magnetic field detected in 2002.'
}, {
  id: 'NGC2024-3',
  name: 'NGC 2024-3',
  alt: 'IRS 2b',
  cls: 'B0.5V',
  spectral: 'B',
  core: 'bgiant',
  lum: 2,
  mods: ['nebulosity'],
  mag: '−1.02',
  ra: '05h 41m 45.8s',
  dec: '−01° 54′ 29″',
  dist: '414 pc',
  status: 'caution',
  field: 'F-07',
  teff: '28,400',
  radius: '7.2',
  notes: 'Heavily reddened. Photometry from this field carries a 0.4 mag extinction correction.'
}, {
  id: 'BMOri',
  name: 'V* BM Ori',
  alt: 'θ¹ Ori B',
  cls: 'B3V',
  spectral: 'B',
  core: 'ms',
  lum: 3,
  mods: ['variable', 'companion2'],
  mag: '+8.06',
  ra: '05h 35m 16.1s',
  dec: '−05° 23′ 07″',
  dist: '389 pc',
  status: 'fault',
  field: 'F-04',
  teff: '18,600',
  radius: '3.1',
  notes: 'Eclipsing binary, period 6.47 d. Detector lost sync mid-egress at 22:18 UTC.'
}, {
  id: 'PROPLYD177',
  name: '177-341W',
  alt: '—',
  cls: 'M2',
  spectral: 'M',
  core: 'proto',
  lum: 5,
  mods: ['planets'],
  mag: '+15.4',
  ra: '05h 35m 17.7s',
  dec: '−05° 23′ 41″',
  dist: '414 pc',
  status: 'nominal',
  field: 'F-07',
  teff: '3,550',
  radius: '1.9',
  notes: 'Photoevaporating disc. Resolved silhouette in three bands.'
}, {
  id: 'GD165B',
  name: 'GD 165B',
  alt: '—',
  cls: 'L4',
  spectral: 'L',
  core: 'browndwarf',
  lum: 6,
  mods: [],
  mag: '+19.2',
  ra: '14h 24m 39.1s',
  dec: '+09° 17′ 10″',
  dist: '31.7 pc',
  status: 'archive',
  field: 'F-11',
  teff: '1,750',
  radius: '0.11',
  notes: 'Prototype L dwarf. Archived after the 2024 recalibration.'
}, {
  id: 'SIRB',
  name: 'Sirius B',
  alt: 'α CMa B',
  cls: 'DA2',
  spectral: 'A',
  core: 'wd',
  lum: 6,
  mods: ['companion'],
  mag: '+8.44',
  ra: '06h 45m 08.9s',
  dec: '−16° 42′ 58″',
  dist: '2.64 pc',
  status: 'nominal',
  field: 'F-02',
  teff: '25,200',
  radius: '0.008',
  notes: 'Astrometric reference. Solution stable to 0.9 mas since 2019.'
}, {
  id: 'CygX1',
  name: 'Cygnus X-1',
  alt: 'HDE 226868',
  cls: 'O9.7Iab',
  spectral: 'Y',
  core: 'bh',
  lum: 1,
  mods: ['accretion', 'jets'],
  mag: '+8.95',
  ra: '19h 58m 21.7s',
  dec: '+35° 12′ 06″',
  dist: '2.22 kpc',
  status: 'nominal',
  field: 'F-19',
  teff: '—',
  radius: '—',
  notes: 'Accreting stellar-mass black hole. X-ray state transitions tracked hourly.'
}, {
  id: 'CRAB',
  name: 'PSR B0531+21',
  alt: 'Crab pulsar',
  cls: '—',
  spectral: 'T',
  core: 'ns',
  lum: 2,
  mods: ['beams', 'magnetic'],
  mag: '+16.5',
  ra: '05h 34m 31.9s',
  dec: '+22° 00′ 52″',
  dist: '2.0 kpc',
  status: 'nominal',
  field: 'F-05',
  teff: '—',
  radius: '—',
  notes: 'Period 33.5 ms, spin-down measured continuously since ingest start.'
}, {
  id: 'PROXCEN',
  name: 'Proxima Centauri',
  alt: 'α Cen C',
  cls: 'M5.5Ve',
  spectral: 'M',
  core: 'dwarf',
  lum: 6,
  mods: ['flare', 'planets'],
  mag: '+11.13',
  ra: '14h 29m 43.0s',
  dec: '−62° 40′ 46″',
  dist: '1.30 pc',
  status: 'nominal',
  field: 'F-22',
  teff: '3,042',
  radius: '0.15',
  notes: 'Flare monitoring active. Three confirmed planets in the catalogue.'
}, {
  id: 'BETELG',
  name: 'Betelgeuse',
  alt: 'α Ori',
  cls: 'M1-2Ia',
  spectral: 'M',
  core: 'hyper',
  lum: 1,
  mods: ['variable', 'nebulosity'],
  mag: '+0.42',
  ra: '05h 55m 10.3s',
  dec: '+07° 24′ 25″',
  dist: '168 pc',
  status: 'caution',
  field: 'F-07',
  teff: '3,600',
  radius: '764',
  notes: 'Semi-regular variable. Saturated in two of four detectors; use the short-exposure set.'
}];
const FIELDS = [{
  id: 'F-02',
  name: 'Sirius reference',
  objects: 38,
  status: 'nominal'
}, {
  id: 'F-04',
  name: 'Trapezium core',
  objects: 214,
  status: 'fault'
}, {
  id: 'F-05',
  name: 'Crab region',
  objects: 96,
  status: 'nominal'
}, {
  id: 'F-07',
  name: 'Deep field 07',
  objects: 1847,
  status: 'caution'
}, {
  id: 'F-11',
  name: 'L dwarf survey',
  objects: 512,
  status: 'archive'
}, {
  id: 'F-19',
  name: 'Cyg X complex',
  objects: 143,
  status: 'nominal'
}, {
  id: 'F-22',
  name: 'Southern proper motion',
  objects: 409,
  status: 'nominal'
}];
const QUEUE = [{
  id: 'Q-118',
  target: 'Deep field 07',
  frames: 12,
  done: 4,
  exp: '1200 s',
  eta: '06:40 UTC',
  state: 'running'
}, {
  id: 'Q-119',
  target: 'Trapezium core',
  frames: 8,
  done: 0,
  exp: '600 s',
  eta: '08:05 UTC',
  state: 'queued'
}, {
  id: 'Q-117',
  target: 'Crab region',
  frames: 6,
  done: 6,
  exp: '900 s',
  eta: '—',
  state: 'complete'
}, {
  id: 'Q-116',
  target: 'L dwarf survey',
  frames: 20,
  done: 3,
  exp: '1800 s',
  eta: '—',
  state: 'halted'
}];
Object.assign(window, {
  SPRITE,
  OBJECTS,
  FIELDS,
  QUEUE
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/atlas/catalog-data.js", error: String((e && e.message) || e) }); }

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.Dialog = __ds_scope.Dialog;

__ds_ns.IconButton = __ds_scope.IconButton;

__ds_ns.Tabs = __ds_scope.Tabs;

__ds_ns.Tag = __ds_scope.Tag;

__ds_ns.Tooltip = __ds_scope.Tooltip;

__ds_ns.DataTable = __ds_scope.DataTable;

__ds_ns.Meter = __ds_scope.Meter;

__ds_ns.Readout = __ds_scope.Readout;

__ds_ns.SPRITE_URL = __ds_scope.SPRITE_URL;

__ds_ns.SPECTRAL_COLORS = __ds_scope.SPECTRAL_COLORS;

__ds_ns.CORES = __ds_scope.CORES;

__ds_ns.MODIFIERS = __ds_scope.MODIFIERS;

__ds_ns.StarIcon = __ds_scope.StarIcon;

__ds_ns.StatusDot = __ds_scope.StatusDot;

__ds_ns.Checkbox = __ds_scope.Checkbox;

__ds_ns.Input = __ds_scope.Input;

__ds_ns.Select = __ds_scope.Select;

__ds_ns.Switch = __ds_scope.Switch;

})();
