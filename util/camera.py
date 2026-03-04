import carla

class CameraParameters:
    def __init__(self):
        self.x = 1
        self.y = 0
        self.z = 1.4
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        self.lens_circle_falloff = '5.0'
        self.lens_circle_multiplier = '0.0'
        self.lens_k = '0.0'
        self.lens_kcube = '0.0'
        self.lens_x_size = '0.08'
        self.lens_y_size = '0.08'
        self.bloom_intensity = 0.675
        self.fov = 90.0
        self.fstop = 1.4
        self.iso = 100.0
        self.gamma = 2.2
        self.lens_flare_intensity = 0.1
        self.sensor_tick = 0.0
        self.shutter_speed = 200.0
        self.exposure_compensation = 0.0
        self.motion_blur_intensity = 0.45
        self.motion_blur_max_distortion = 0.35
        self.chromatic_aberration_intensity = 0.0
        self.temp = 6500.0
        self.tint = 0.0
        self.blur_amount = 1.0

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'pitch': self.pitch,
            'yaw': self.yaw,
            'roll': self.roll,
            'lens_circle_falloff': self.lens_circle_falloff,
            'lens_circle_multiplier': self.lens_circle_multiplier,
            'lens_k': self.lens_k,
            'lens_kcube': self.lens_kcube,
            'lens_x_size': self.lens_x_size,
            'lens_y_size': self.lens_y_size,
            'bloom_intensity': self.bloom_intensity,
            'fov': self.fov,
            'fstop': self.fstop,
            'iso': self.iso,
            'gamma': self.gamma,
            'lens_flare_intensity': self.lens_flare_intensity,
            'sensor_tick': self.sensor_tick,
            'shutter_speed': self.shutter_speed,
            'exposure_compensation': self.exposure_compensation,
            'motion_blur_intensity': self.motion_blur_intensity,
            'motion_blur_max_distortion' : self.motion_blur_max_distortion,
            'chromatic_aberration_intensity': self.chromatic_aberration_intensity,
            'temp': self.temp,
            'tint': self.tint,
            'blur_amount': self.blur_amount
        }


def update_camera_params(camera_params, case):
    """
    Update camera parameters based on a case.
    """
    camera_params.x = case[0]
    camera_params.y = case[1]
    camera_params.z = case[2]
    camera_params.pitch = case[3]
    camera_params.roll = case[4]
    camera_params.lens_circle_multiplier = case[5]
    camera_params.bloom_intensity = case[6]
    camera_params.fov = case[7]
    camera_params.gamma = case[8]
    camera_params.motion_blur_intensity = case[9][0]
    camera_params.motion_blur_max_distortion = case[9][1]
    camera_params.sensor_tick = 0.5 #this one is only for control FPS, not parameters
    camera_params.exposure_compensation = case[10]
    camera_params.chromatic_aberration_intensity = case[11]
    camera_params.temp = case[12]
    camera_params.tint = case[13]

def setup_camera(world, main_vehicle, camera_params):
    """
    Set up the camera with given parameters.
    """
    blueprint_library = world.get_blueprint_library()
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))

    # Modify camera parameters
    camera_transform = change_camera_x(camera_transform, camera_params.x)
    camera_transform = change_camera_y(camera_transform, camera_params.y)
    camera_transform = change_camera_z(camera_transform, camera_params.z)
    camera_transform = change_camera_pitch(camera_transform, camera_params.pitch)
    camera_transform = change_camera_yaw(camera_transform, camera_params.yaw)
    camera_transform = change_camera_roll(camera_transform, camera_params.roll)

    change_lens_circle_falloff(camera_bp, camera_params.lens_circle_falloff)
    change_lens_circle_multiplier(camera_bp, camera_params.lens_circle_multiplier)
    change_lens_k(camera_bp, camera_params.lens_k)
    change_lens_kcube(camera_bp, camera_params.lens_kcube)
    change_lens_x_size(camera_bp, camera_params.lens_x_size)
    change_lens_y_size(camera_bp, camera_params.lens_y_size)

    change_bloom_intensity(camera_bp, camera_params.bloom_intensity)
    change_fov(camera_bp, camera_params.fov)
    change_fstop(camera_bp, camera_params.fstop)
    change_iso(camera_bp, camera_params.iso)
    change_gamma(camera_bp, camera_params.gamma)
    change_lens_flare_intensity(camera_bp, camera_params.lens_flare_intensity)
    change_sensor_tick(camera_bp, camera_params.sensor_tick)
    change_shutter_speed(camera_bp, camera_params.shutter_speed)

    change_exposure_compensation(camera_bp, camera_params.exposure_compensation)
    change_motion_blur_max_distortion(camera_bp, camera_params.motion_blur_max_distortion)
    change_motion_blur_intensity(camera_bp, camera_params.motion_blur_intensity)
    change_chromatic_aberration_intensity(camera_bp, camera_params.chromatic_aberration_intensity)
    change_temp(camera_bp, camera_params.temp)
    change_tint(camera_bp, camera_params.tint)
    change_blur_amount(camera_bp, camera_params.blur_amount)

    # camera_bp.set_attribute('image_size_x', '1200')  # 设置宽度
    # camera_bp.set_attribute('image_size_y', '1200')  # 设置高度
    return world.spawn_actor(camera_bp, camera_transform, attach_to=main_vehicle)

def setup_depth_camera(world, main_vehicle, camera_params):
    """
    Set up the camera with given parameters.
    """
    blueprint_library = world.get_blueprint_library()
    camera_bp = blueprint_library.find('sensor.camera.depth')
    camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))

    # Modify camera parameters
    camera_transform = change_camera_x(camera_transform, camera_params.x)
    camera_transform = change_camera_y(camera_transform, camera_params.y)
    camera_transform = change_camera_z(camera_transform, camera_params.z)
    camera_transform = change_camera_pitch(camera_transform, camera_params.pitch)
    camera_transform = change_camera_yaw(camera_transform, camera_params.yaw)
    camera_transform = change_camera_roll(camera_transform, camera_params.roll)

    change_lens_circle_falloff(camera_bp, camera_params.lens_circle_falloff)
    change_lens_circle_multiplier(camera_bp, camera_params.lens_circle_multiplier)
    change_lens_k(camera_bp, camera_params.lens_k)
    change_lens_kcube(camera_bp, camera_params.lens_kcube)
    change_lens_x_size(camera_bp, camera_params.lens_x_size)
    change_lens_y_size(camera_bp, camera_params.lens_y_size)

    change_fov(camera_bp, camera_params.fov)
    #change_bloom_intensity(camera_bp, camera_params.bloom_intensity)
    #change_fstop(camera_bp, camera_params.fstop)
    #change_iso(camera_bp, camera_params.iso)
    #change_gamma(camera_bp, camera_params.gamma)
    #change_lens_flare_intensity(camera_bp, camera_params.lens_flare_intensity)
    change_sensor_tick(camera_bp, camera_params.sensor_tick)
    #change_shutter_speed(camera_bp, camera_params.shutter_speed)

    #change_exposure_compensation(camera_bp, camera_params.exposure_compensation)
    #change_motion_blur_intensity(camera_bp, camera_params.motion_blur_intensity)
    #change_chromatic_aberration_intensity(camera_bp, camera_params.chromatic_aberration_intensity)
    #change_temp(camera_bp, camera_params.temp)
    #change_tint(camera_bp, camera_params.tint)
    #change_blur_amount(camera_bp, camera_params.blur_amount)

    # camera_bp.set_attribute('image_size_x', '1200')  
    # camera_bp.set_attribute('image_size_y', '1200')  

    return world.spawn_actor(camera_bp, camera_transform, attach_to=main_vehicle)

def change_lens_circle_falloff(camera_blueprint, falloff_value):
    """
    Change the lens_circle_falloff parameter of the camera.

    :param camera_blueprint: Camera blueprint
    :param falloff_value: The lens_circle_falloff value to set (string format)
    """
    try:
        camera_blueprint.set_attribute('lens_circle_falloff', falloff_value)
        print(f"Camera : lens_circle_falloff has been changed to {falloff_value}")
    except Exception as e:
        print(f"Error changing lens_circle_falloff: {e}")

def change_lens_circle_multiplier(camera_blueprint, multiplier_value):
    """
    Change the lens_circle_multiplier parameter of the camera.

    :param camera_blueprint: Camera blueprint
    :param multiplier_value: The lens_circle_multiplier value to set (string format)
    """
    try:
        camera_blueprint.set_attribute('lens_circle_multiplier', str(multiplier_value))
        print(f"Camera : lens_circle_multiplier has been changed to {multiplier_value}")
    except Exception as e:
        print(f"Error changing lens_circle_multiplier: {e}")

def change_lens_k(camera_blueprint, k_value):
    """
    Change the lens_k parameter of the camera.

    :param camera_blueprint: Camera blueprint
    :param k_value: The lens_k value to set (string format)
    """
    try:
        camera_blueprint.set_attribute('lens_k', k_value)
        print(f"Camera : lens_k has been changed to {k_value}")
    except Exception as e:
        print(f"Error changing lens_k: {e}")

def change_lens_kcube(camera_blueprint, kc_value):
    """
    Change the lens_kcube parameter of the camera.

    :param camera_blueprint: Camera blueprint
    :param kc_value: The lens_kcube value to set (string format)
    """
    try:
        camera_blueprint.set_attribute('lens_kcube', kc_value)
        print(f"Camera : lens_kcube has been changed to {kc_value}")
    except Exception as e:
        print(f"Error changing lens_kcube: {e}")

def change_lens_x_size(camera_blueprint, x_size_value):
    """
    Change the lens_x_size parameter of the camera.

    :param camera_blueprint: Camera blueprint
    :param x_size_value: The lens_x_size value to set (string format)
    """
    try:
        camera_blueprint.set_attribute('lens_x_size', x_size_value)
        print(f"Camera : lens_x_size has been changed to {x_size_value}")
    except Exception as e:
        print(f"Error changing lens_x_size: {e}")

def change_lens_y_size(camera_blueprint, y_size_value):
    """
    Change the lens_y_size parameter of the camera.

    :param camera_blueprint: Camera blueprint
    :param y_size_value: The lens_y_size value to set (string format)
    """
    try:
        camera_blueprint.set_attribute('lens_y_size', y_size_value)
        print(f"Camera : lens_y_size has been changed to {y_size_value}")
    except Exception as e:
        print(f"Error changing lens_y_size: {e}")

def change_camera_x(camera_transform, new_x):
    """
    Change the x position of the camera
    :param camera_transform: The original camera Transform object
    :param new_x: The new x value
    :return: The modified camera Transform object
    """
    try:
        new_location = carla.Location(x=new_x, y=camera_transform.location.y, z=camera_transform.location.z)
        print(f"Camera : X position has been changed to {new_x}")
        return carla.Transform(new_location, camera_transform.rotation)
    except Exception as e:
        print(f"Error changing camera X position: {e}")

def change_camera_y(camera_transform, new_y):
    """
    Change the y position of the camera
    :param camera_transform: The original camera Transform object
    :param new_y: The new y value
    :return: The modified camera Transform object
    """
    try:
        new_location = carla.Location(x=camera_transform.location.x, y=new_y, z=camera_transform.location.z)
        print(f"Camera : Y position has been changed to {new_y}")
        return carla.Transform(new_location, camera_transform.rotation)
    except Exception as e:
        print(f"Error changing camera Y position: {e}")

def change_camera_z(camera_transform, new_z):
    """
    Change the z position (height) of the camera
    :param camera_transform: The original camera Transform object
    :param new_z: The new z value
    :return: The modified camera Transform object
    """
    try:
        new_location = carla.Location(x=camera_transform.location.x, y=camera_transform.location.y, z=new_z)
        print(f"Camera : Z position has been changed to {new_z}")
        return carla.Transform(new_location, camera_transform.rotation)
    except Exception as e:
        print(f"Error changing camera Z position: {e}")

def change_camera_yaw(camera_transform, new_yaw):
    """
    Change the yaw of the camera.
    :param camera_transform: The original camera Transform object.
    :param new_yaw: The new yaw value.
    :return: The modified camera Transform object.
    """
    try:
        new_location = camera_transform.location
        new_rotation = carla.Rotation(pitch=camera_transform.rotation.pitch, yaw=new_yaw, roll=camera_transform.rotation.roll)
        print(f"Camera : Yaw has been changed to {new_yaw}")
        return carla.Transform(new_location, new_rotation)
    except Exception as e:
        print(f"Error changing camera Yaw: {e}")

def change_camera_pitch(camera_transform, new_pitch):
    """
    Change the pitch of the camera.
    :param camera_transform: The original camera Transform object.
    :param new_pitch: The new pitch value.
    :return: The modified camera Transform object.
    """
    try:
        new_location = camera_transform.location
        new_rotation = carla.Rotation(pitch=new_pitch, yaw=camera_transform.rotation.yaw, roll=camera_transform.rotation.roll)
        print(f"Camera : Pitch has been changed to {new_pitch}")
        return carla.Transform(new_location, new_rotation)
    except Exception as e:
        print(f"Error changing camera Pitch: {e}")

def change_camera_roll(camera_transform, new_roll):
    """
    Change the roll of the camera.
    :param camera_transform: The original camera Transform object.
    :param new_roll: The new roll value.
    :return: The modified camera Transform object.
    """
    try:
        new_location = camera_transform.location
        new_rotation = carla.Rotation(pitch=camera_transform.rotation.pitch, yaw=camera_transform.rotation.yaw, roll=new_roll)
        print(f"Camera : Roll has been changed to {new_roll}")
        return carla.Transform(new_location, new_rotation)
    except Exception as e:
        print(f"Error changing camera Roll: {e}")

def change_bloom_intensity(camera_blueprint, bloom_intensity):
    """
    Change the bloom intensity of the camera.
    """
    try:
        camera_blueprint.set_attribute('bloom_intensity', str(bloom_intensity))
        print(f"Camera : bloom intensity has been changed to: {bloom_intensity}")
    except Exception as e:
        print(f"Error changing bloom intensity: {e}")

def change_fov(camera_blueprint, new_fov):
    """
    Change the focal length (field of view) of the camera.

    :param camera: The camera object whose focal length is to be changed.
    :param new_focal_length: The new focal length value (field of view, in degrees).
    """

    try:
        camera_blueprint.set_attribute('fov', str(new_fov))
        print(f"Camera : fov has been changed to: {new_fov} degrees")
    except Exception as e:
        print(f"Error changing fov: {e}")

def change_fstop(camera_blueprint, fstop):
    """
    Change the f-stop of the camera.
    """
    try:
        camera_blueprint.set_attribute('fstop', str(fstop))
        print(f"Camera : f-stop has been changed to: {fstop}")
    except Exception as e:
        print(f"Error changing f-stop: {e}")

def change_iso(camera_blueprint, iso):
    """
    Change the ISO sensitivity of the camera.
    """
    try:
        camera_blueprint.set_attribute('iso', str(iso))
        print(f"Camera : ISO has been changed to: {iso}")
    except Exception as e:
        print(f"Error changing ISO: {e}")

def change_gamma(camera_blueprint, gamma):
    """
    Change the gamma of the camera.
    """
    try:
        camera_blueprint.set_attribute('gamma', str(gamma))
        print(f"Camera : gamma has been changed to: {gamma}")
    except Exception as e:
        print(f"Error changing gamma: {e}")

def change_lens_flare_intensity(camera_blueprint, lens_flare_intensity):
    """
    Change the lens flare intensity of the camera.
    """
    try:
        camera_blueprint.set_attribute('lens_flare_intensity', str(lens_flare_intensity))
        print(f"Camera : lens flare intensity has been changed to: {lens_flare_intensity}")
    except Exception as e:
        print(f"Error changing lens flare intensity: {e}")

def change_sensor_tick(camera_blueprint, sensor_tick):
    """
    Change the sensor tick of the camera.
    """
    try:
        camera_blueprint.set_attribute('sensor_tick', str(sensor_tick))
        print(f"Camera : sensor tick has been changed to: {sensor_tick}")
    except Exception as e:
        print(f"Error changing sensor tick: {e}")

def change_shutter_speed(camera_blueprint, shutter_speed):
    """
    Change the shutter speed of the camera.
    """
    try:
        camera_blueprint.set_attribute('shutter_speed', str(shutter_speed))
        print(f"Camera : shutter speed has been changed to: {shutter_speed}")
    except Exception as e:
        print(f"Error changing shutter speed: {e}")

def change_exposure_compensation(camera_blueprint, exposure_value):
    """
    Change the exposure compensation of the camera.
    """
    try:
        camera_blueprint.set_attribute('exposure_compensation', str(exposure_value))
        print(f"Camera : exposure compensation has been changed to: {exposure_value}")
    except Exception as e:
        print(f"Error changing exposure compensation: {e}")

def change_motion_blur_intensity(camera_blueprint, intensity):
    """
    Change the motion blur intensity of the camera.
    """
    try:
        camera_blueprint.set_attribute('motion_blur_intensity', str(intensity))
        print(f"Camera : motion blur intensity has been changed to: {intensity}")
    except Exception as e:
        print(f"Error changing motion blur intensity: {e}")

def change_motion_blur_max_distortion(camera_blueprint, distortion):
    """
    Change the motion blur max distortion of the camera.
    """
    try:
        camera_blueprint.set_attribute('motion_blur_max_distortion', str(distortion))
        print(f"Camera : motion blur max distortion has been changed to: {distortion}")
    except Exception as e:
        print(f"Error changing motion blur max distortion: {e}")


def change_chromatic_aberration_intensity(camera_blueprint, intensity):
    """
    Change the chromatic aberration intensity of the camera.
    """
    try:
        camera_blueprint.set_attribute('chromatic_aberration_intensity', str(intensity))
        print(f"Camera : chromatic aberration intensity has been changed to: {intensity}")
    except Exception as e:
        print(f"Error changing chromatic aberration intensity: {e}")

def change_temp(camera_blueprint, temperature):
    """
    Change the temperature of the camera for white balance.
    """
    try:
        camera_blueprint.set_attribute('temp', str(temperature))
        print(f"Camera : temperature has been changed to: {temperature}")
    except Exception as e:
        print(f"Error changing temperature: {e}")

def change_tint(camera_blueprint, tint_value):
    """
    Change the tint of the camera for white balance.
    """
    try:
        camera_blueprint.set_attribute('tint', str(tint_value))
        print(f"Camera : tint has been changed to: {tint_value}")
    except Exception as e:
        print(f"Error changing tint: {e}")

def change_blur_amount(camera_blueprint, blur_value):
    """
    Change the blur amount of the camera.
    """
    try:
        camera_blueprint.set_attribute('blur_amount', str(blur_value))
        print(f"Camera : blur amount has been changed to: {blur_value}")
    except Exception as e:
        print(f"Error changing blur amount: {e}")

