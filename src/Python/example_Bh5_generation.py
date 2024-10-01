# -*- coding: utf-8 -*-
import h5py
import numpy as np
import datetime

#define enums
Brillouin_signal_type_enum = h5py.enum_dtype({'other':0, 'spontaneous':1, 'stimulated':2, 'time_resolved':3}, basetype='i')
Scanning_strategy_enum = h5py.enum_dtype({'other':0, 'point_scanning':1, 'line_scanning':2, 'lightsheet':3, 'time_resolved':4}, basetype='i')
Spectrometer_type_enum = h5py.enum_dtype({'other':0, 'VIPA':1, 'FP':2, 'lock-in':3, 'heterodyne':4, 'time_domain':5}, basetype='i')
Immersion_medium_enum = h5py.enum_dtype({'other':0, 'air':1, 'water':2, 'oil':3}, basetype='i')

Fit_model_enum = h5py.enum_dtype({'other':0, 'Lorentzian':1, 'DHO':2, 'Voigt':3}, basetype='i')

def lorentzian(x, x0, w):
    return 1/(1+((x-x0)/(w/2))**2)

# Create a new HDF5 file
with h5py.File('example.bh5', 'w') as f:
    
    # 1. Create the root group and add attributes
    f.attrs['Version'] = '0.1'
    f.attrs.create('SubTypeID',0,dtype=np.uint32) # Default subtype
    
    # 2. Create the '/Experiment_info' group and add attributes
    exp_info = f.create_group('Experiment_info')
    exp_info.attrs.create('Brillouin_signal_type', 1, dtype=Brillouin_signal_type_enum)
    exp_info.attrs.create('Scanning_strategy', 1, dtype=Scanning_strategy_enum)
    exp_info.attrs.create('Spectrometer_type', 1, dtype=Spectrometer_type_enum)
    exp_info.attrs['Spectral_resolution_MHz'] = 256.0
    exp_info.attrs['Acquisition_time_ms'] = 100.0
    exp_info.attrs['Wavelength_nm'] = 532.0  
    exp_info.attrs['Laser_model'] = 'Torus 532, Novanta'
    exp_info.attrs['Power_mW'] = 5.0 
    exp_info.attrs['Lens_NA'] = 1.1 # detection numerical aperture (same as illumination, unless 'Lens_NA_illum’illum' is specified)
    exp_info.attrs['scattering_angle_deg'] = 180.0  # Epidetection
    exp_info.attrs.create('Immersion_medium', 3, dtype=Immersion_medium_enum)
    exp_info.attrs['Objective_model'] = 'Zeiss Plan-Apochromat 40x/1.1 Oil'
    exp_info.attrs['Temperature_C'] = 21.4
    exp_info.attrs['Temperature_uncertainty_C'] = 0.3
    exp_info.attrs['Datetime'] = datetime.datetime.now().isoformat()  # Current time in ISO 8601 format
    exp_info.attrs['Info'] = 'The experiment was performed by placing the sample on a coverslip...'
    
    
    # 3. Add optional group '/Experiment_info/Spectrometer_characterization'
    spec_char = exp_info.create_group('Spectrometer_characterization')
    freq_GHz = np.linspace(-2, 2)  # Example frequency axis
    irf = lorentzian(freq_GHz, 0, 1e-3*exp_info.attrs['Spectral_resolution_MHz'])  # Example impulse response function (IRF)
    dset_irf = spec_char.create_dataset('IRF', data=irf)
    dset_irf.attrs['Frequency_GHz'] = freq_GHz
    
    # 4. Create '/tn' groups (for timepoints or other measurements)
    for n in range(3):
        tn = f.create_group('t'+str(n))
        tn.attrs['Datetime'] = (datetime.datetime.now()++datetime.timedelta(hours=n*1.5)).isoformat()
        
        # 5. Create the '/tn/Analyzed_data' group and datasets
        
        Nx, Ny, Nz = (20, 30, 3) # Number of points in x,y,z
        dx, dy, dz = (0.5, 0.5, 2) # Stepsizes (in um)
        analyzed_data = tn.create_group('Analyzed_data')
        n_points = Nx*Ny*Nz  # total number of points
        
        # indices
        analyzed_data.create_dataset('Index', data=np.arange(n_points))
        
        # Example spatial positions (x, y, z)
        X, Y, Z = np.meshgrid(dx*np.arange(Nx), dy*np.arange(Ny), dz*np.arange(Nz))
        spatial_pos = np.zeros(n_points, dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])
        spatial_pos['x'] = X.flatten()
        spatial_pos['y'] = Y.flatten()
        spatial_pos['z'] = Z.flatten()
        analyzed_data.create_dataset('Spatial_position_um', data=spatial_pos)
        
        # Example spectral parameters (Shift, Width, Amplitude)
        analyzed_data.create_dataset('Shift_0_GHz', data=7.4+np.random.random(n_points) * 0.01)  # Shift in GHz
        analyzed_data.create_dataset('Width_0_GHz', data=0.4+np.random.random(n_points) * 0.03)  # Width in GHz
        analyzed_data.create_dataset('Amplitude_0', data=100+np.random.random(n_points) * 3)  # Amplitude
        # Example fit errors
        fit_err = analyzed_data.create_dataset('Fit_error_0', shape=(n_points,), dtype=np.dtype([('R2', 'f'), ('RMSE', 'f')]))  
        fit_err['R2'] = np.random.random(n_points)
        fit_err['RMSE'] = 10*np.random.random(n_points)
        
        # Calibration index assuming one new calibration is acquired every cal_freq spectra
        cal_freq = 150
        analyzed_data.create_dataset('Calibration_index', data=np.arange(n_points) // cal_freq)
        
        # Timestamp
        analyzed_data.create_dataset('Timestamp_ms', data=exp_info.attrs['Acquisition_time_ms']*np.arange(n_points))
        
        # Add attributes to Analyzed_data
        analyzed_data.attrs.create('Fit_model', 1, dtype=Fit_model_enum)
        analyzed_data.attrs['Corrections'] = 'The NA correction is done by dividing the measured shift by 1.xx'
        
        # 6. Create '/tn/Spectra' group
        spectra = tn.create_group('Spectra')
        
        # Example Amplitude dataset (2D: points x frequency)
        freq_GHz = np.linspace(6, 9, 45)  # 45 frequency points
        amplitude = np.empty((n_points, len(freq_GHz)))
        for i in range(n_points):
            spectrum = lorentzian(freq_GHz, analyzed_data['Shift_0_GHz'][i], analyzed_data['Width_0_GHz'][i])
            amplitude[i,:] = spectrum
        spectra.create_dataset('Amplitude', data=amplitude)
        
        # Example Frequency dataset (1D frequency axis)
        dset_freq = spectra.create_dataset('Frequency', data=freq_GHz)
        dset_freq.attrs['Unit'] = 'GHz'
        
        # 7. Optional: Create '/tn/Images' group
        def add_attrs_for_images(ds, pixel_size):
            ds.attrs.create('CLASS','IMAGE', dtype='S5')
            ds.attrs.create('DISPLAY_ORIGIN','UL', dtype='S2')
            ds.attrs.create('IMAGE_VERSION','1.2', dtype='S3')
            ds.attrs['element_size_um']=pixel_size
        px_size = [dz, dy, dx]
        images = tn.create_group('Images')
        images.create_dataset('Index', data=np.reshape(analyzed_data['Index'], (Nz,Ny,Nx))) 
        ds = images.create_dataset('Shift_0_GHz', data=np.reshape(analyzed_data['Shift_0_GHz'], (Nz,Ny,Nx)))
        add_attrs_for_images(ds, px_size)
        ds = images.create_dataset('Width_0_GHz', data=np.reshape(analyzed_data['Width_0_GHz'], (Nz,Ny,Nx))) 
        add_attrs_for_images(ds, px_size)
        ds = images.create_dataset('Amplitude_0', data=np.reshape(analyzed_data['Amplitude_0'], (Nz,Ny,Nx))) 
        add_attrs_for_images(ds, px_size)
        
        # 8. Optional: Create '/tn/Calibration_spectra' group
        calibration_spectra = tn.create_group('Calibration_spectra')
        
        if n > 0:
            calibration_spectra.attrs['same_as'] = '/t0'
        else:   
            calibration_spectra.attrs['Description'] = 'The calibration is performed by acquiring water...'
            calibration_spectra.attrs['Shift_0_GHz'] = 7.46
            cal_indices = np.unique(analyzed_data['Calibration_index'])  
            for i in range(len(cal_indices)):                 
                calib_data = lorentzian(freq_GHz, calibration_spectra.attrs['Shift_0_GHz'], 0.4)
                dset_calib = calibration_spectra.create_dataset(str(i), data=calib_data)
                



