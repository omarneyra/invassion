class_name CameraOrbit
extends Node3D
## Sistema de Cámara Trackball Virtual con Inercia (Momentum),
## Zoom responsivo (Rueda, Gestos, Teclado, Botones HUD) y Auto-Enfoque a objetivos.

@export var target_distance: float = 16.0
@export var min_distance: float = 7.2
@export var max_distance: float = 34.0
@export var rotation_sensitivity: float = 0.004
@export var zoom_step: float = 2.5
@export var zoom_smoothness: float = 14.0
@export var drag_threshold: float = 4.0
@export var inertia_friction: float = 5.0 # Tasa de frenado de inercia

@onready var camera: Camera3D = $Camera3D

var _is_left_dragging: bool = false
var _is_right_dragging: bool = false
var _press_pos: Vector2 = Vector2.ZERO
var _has_dragged_past_threshold: bool = false
var _current_distance: float = 14.0

var _angular_velocity: Vector2 = Vector2.ZERO

var _is_focusing: bool = false
var _focus_target_basis: Basis
var _focus_speed: float = 5.0

signal clicked_screen(screen_pos: Vector2)

func _ready() -> void:
	_current_distance = target_distance
	if camera:
		camera.position = Vector3(0.0, 0.0, _current_distance)

func _process(delta: float) -> void:
	# 1. Suavizado de zoom
	_current_distance = lerpf(_current_distance, target_distance, delta * zoom_smoothness)
	if camera:
		camera.position.z = _current_distance

	# 2. Manejo de auto-enfoque a objetivo
	if _is_focusing:
		var current_quat = basis.get_rotation_quaternion()
		var target_quat = _focus_target_basis.get_rotation_quaternion()
		var new_quat = current_quat.slerp(target_quat, delta * _focus_speed)
		basis = Basis(new_quat).orthonormalized()

		if current_quat.dot(target_quat) > 0.999:
			_is_focusing = false

	# 3. Aplicar inercia si no se está arrastrando ni enfocando
	elif not _is_left_dragging and not _is_right_dragging:
		if _angular_velocity.length_squared() > 0.000001:
			_apply_trackball_delta(_angular_velocity * delta * 60.0)
			_angular_velocity = _angular_velocity.lerp(Vector2.ZERO, delta * inertia_friction)
		else:
			_angular_velocity = Vector2.ZERO

func zoom_in(amount: float = -1.0) -> void:
	var step = zoom_step if amount < 0.0 else amount
	target_distance = clampf(target_distance - step, min_distance, max_distance)

func zoom_out(amount: float = -1.0) -> void:
	var step = zoom_step if amount < 0.0 else amount
	target_distance = clampf(target_distance + step, min_distance, max_distance)

func _input(event: InputEvent) -> void:
	# Usar _input para garantizar que el zoom de rueda y gestos nunca sea bloqueado
	if event is InputEventMouseButton:
		var mb: InputEventMouseButton = event
		if mb.is_pressed():
			if mb.button_index == MOUSE_BUTTON_WHEEL_UP:
				zoom_in()
				get_viewport().set_input_as_handled()
			elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
				zoom_out()
				get_viewport().set_input_as_handled()

	elif event is InputEventMagnifyGesture:
		# Pellizco en trackpad / pantalla táctil
		var gesture: InputEventMagnifyGesture = event
		target_distance = clampf(target_distance / gesture.factor, min_distance, max_distance)
		get_viewport().set_input_as_handled()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mouse_event: InputEventMouseButton = event

		if mouse_event.button_index == MOUSE_BUTTON_LEFT:
			if mouse_event.pressed:
				_is_left_dragging = true
				_press_pos = mouse_event.position
				_has_dragged_past_threshold = false
				_angular_velocity = Vector2.ZERO
				_is_focusing = false
			else:
				if _is_left_dragging and not _has_dragged_past_threshold:
					clicked_screen.emit(mouse_event.position)
				_is_left_dragging = false
				_has_dragged_past_threshold = false

		elif mouse_event.button_index == MOUSE_BUTTON_RIGHT:
			if mouse_event.pressed:
				_is_right_dragging = true
				_angular_velocity = Vector2.ZERO
				_is_focusing = false
			else:
				_is_right_dragging = false

	elif event is InputEventMouseMotion:
		var motion_event: InputEventMouseMotion = event

		if _is_left_dragging:
			var delta_dist = motion_event.position.distance_to(_press_pos)
			if not _has_dragged_past_threshold and delta_dist > drag_threshold:
				_has_dragged_past_threshold = true

			if _has_dragged_past_threshold:
				_apply_trackball_motion(motion_event.relative)

		elif _is_right_dragging:
			_apply_trackball_motion(motion_event.relative)

	elif event is InputEventKey and event.pressed and not event.echo:
		# Atajos de teclado para zoom
		if event.keycode == KEY_EQUAL or event.keycode == KEY_KP_ADD or event.keycode == KEY_PAGEUP:
			zoom_in()
		elif event.keycode == KEY_MINUS or event.keycode == KEY_KP_SUBTRACT or event.keycode == KEY_PAGEDOWN:
			zoom_out()

func _apply_trackball_motion(relative: Vector2) -> void:
	var move_delta = relative * rotation_sensitivity
	_apply_trackball_delta(move_delta)
	_angular_velocity = _angular_velocity.lerp(move_delta, 0.45)

func _apply_trackball_delta(move_delta: Vector2) -> void:
	var cam_basis = camera.global_transform.basis if camera else global_transform.basis
	var cam_right = cam_basis.x.normalized()
	var cam_up = cam_basis.y.normalized()

	var b = basis
	if absf(move_delta.x) > 0.00001:
		b = b.rotated(cam_up, -move_delta.x)
	if absf(move_delta.y) > 0.00001:
		b = b.rotated(cam_right, -move_delta.y)

	basis = b.orthonormalized()

func focus_on_point(target_world_pos: Vector3) -> void:
	if target_world_pos.length_squared() < 0.01:
		return

	var dir_to_point = target_world_pos.normalized()
	var up = Vector3.UP
	if absf(dir_to_point.dot(up)) > 0.95:
		up = Vector3.FORWARD

	var target_transform = Transform3D().looking_at(-dir_to_point, up)
	_focus_target_basis = target_transform.basis.orthonormalized()
	_angular_velocity = Vector2.ZERO
	_is_focusing = true
