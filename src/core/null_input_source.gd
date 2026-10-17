class_name NullInputSource
extends InputSource
## Null Object: a fighter without a controller (countdown, match over) simply stands still.


func read_frame() -> InputFrame:
	return InputFrame.new()
