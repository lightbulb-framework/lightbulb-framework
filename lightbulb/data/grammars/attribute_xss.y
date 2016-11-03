S: main 
main: event_exp event_payload  | event_exp geckoanychar event_payload | html_exp src_payload | type_exp
event_exp: FSCommand | onAbort | onActivate | onAfterPrint | onAfterUpdate | onBeforeActivate | onBeforeCopy | onBeforeCut | onBeforeDeactivate | onBeforeEditFocus | onBeforePaste | onBeforePrint | onBeforeUnload | onBeforeUpdate | onBegin | onBlur | onBounce | onCellChange | onChange | onClick | onContextMenu | onControlSelect | onCopy | onCut | onDataAvailable | onDataSetChanged | onDataSetComplete | onDblClick | onDeactivate | onDrag | onDragEnd | onDragLeave | onDragEnter | onDragOver | onDragDrop | onDragStart | onDrop | onEnd | onError | onErrorUpdate | onFilterChange | onFinish | onFocus | onFocusIn | onFocusOut | onHashChange | onHelp | onInput | onKeyDown | onKeyPress | onKeyUp | onLayoutComplete | onLoad | onLoseCapture | onMediaComplete | onMediaError | onMessage | onMouseDown | onMouseEnter | onMouseLeave | onMouseMove | onMouseOut | onMouseOver | onMouseUp | onMouseWheel | onMove | onMoveEnd | onMoveStart | onOffline | onOnline | onOutOfSync | onPaste | onPause | onPopState | onProgress | onPropertyChange | onReadyStateChange | onRedo | onRepeat | onReset | onResize | onResizeEnd | onResizeStart | onResume | onReverse | onRowsEnter | onRowExit | onRowDelete | onRowInserted | onScroll | onSeek | onSelect | onSelectionChange | onSelectStart | onStart | onStop | onStorage | onSyncRestored | onSubmit | onTimeError | onTrackChange | onUndo | onUnload | onURLFlip
geckoanychar: ! | # | $ | % | & | ( | ) | * | ~ | + | - | _ | . | ,| : | ; | ? | [ | / | \ ^ | ` | geckoanychar geckoanychar
html_exp: background | dynsrc | lowsrc | style | datasrc | src | href 
type_exp: type = quote text/javascript quote
event_payload: = quote name ( name ) quote  | = name ( name )
src_payload: = &#1; | = &#00001& | = &#x1A&
quote: ' 
name: A
