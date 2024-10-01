# Proposal for version 0.1 of the .Bh5 file format

## General features:
- The specification defines the minimum set of groups/datasets/attributes that must be implemented. More can be added while still complying with the specs
- The exact name of the fields defined by the specification need to be used (case sensitive)
- Compression and filters to individual datasets can be added since they are handled transparently by the HDF5 library; see [documentation](https://docs.hdfgroup.org/archive/support/HDF5/faq/compression.html)
- Strings must be stored as UTF-8
- Enums start from 0

## Structure:
|   /

|   /Experiment\_info

|   ---- /Spectrometer\_ characterization/IRF [1D float] (optional)

|   /tn/Analyzed\_data

|   ------- /Index [1D int]

|   ------- /Spatial\_position\_um [1D compound]

|   ------- /Shift\_n\_GHz [1D (or more) float]

|   ------- /Width\_n\_GHz [1D (or more) float]

|   ------- /Amplitude\_n [1D (or more) float]

|   ------- /Fit\_error\_n [1D (or more) compound]

|   ------- /Calibration\_index [1D int] (optional)

|   ------- /Timestamp\_ms [1D float] (optional)

|   /tn/Spectra

|   ------- /Amplitude [2D (or more) float]

|   ------- /Frequency [1D (or more) float]

|   /tn/Images (optional)

|   ------- /Shift\_n\_GHz [3D float]

|   ------- /Width\_n\_GHz [3D float]

|   ------- /Amplitude\_n [3D float]

|   /tn/Calibration\_spectra (optional)

|   ------- /n [1D float]

## Detailed description of the content of the file:
- ‘/’ (root group) must have the following attributes:
  - **‘Version’ [String]**: version of the specification that the current file is complying with (e.g. ‘0.1’); the numbering should follow the conventions of [semantic versioning](https://semver.org/)
  - **‘SubTypeID’ [uint32]**: identifier of the specific subtype .Bh5 file that is being used. ID 0x00000000 to 0x7FFFFFFF have to be agreed upon and defined on the specifications, while 0x80000000 to 0xFFFFFFFF are free to use as custom subtypes; default is 0
- **‘/Experiment\_info’** (group) has the following attributes:
  - **‘Brillouin\_signal\_type’ [enum {other, spontaneous, stimulated, time\_resolved}]**
  - **‘Scanning\_strategy’ [enum {other, point\_scanning, line\_scanning, lightsheet, time\_resolved}]**
  - **‘Spectrometer\_type’ [enum{other, VIPA, FP, lock-in, heterodyne, time\_domain}]**
  - **‘Spectral\_resolution\_MHz’ [float]**
  - **‘Acquisition\_time\_ms’ [float]**: the time that takes to acquire a single ‘unit’, which is different depending on the scanning strategy (i.e. point, line, plane, A-line, etc.)
  - **‘Wavelength\_nm’ [float]**: wavelength of the laser used for the measurements
  - **‘Laser\_model’ [string]** (optional)
  - **‘Power\_mW’ [float]**: total optical power on the sample
  - **‘Lens\_NA’ [float]**: the numerical aperture of the lens that is used for imaging (detection)
  - **Lens\_NA\_illum’ [float]** (optional): the numerical aperture of the lens that is used for illumination (if different from detection)
  - **‘scattering\_angle\_deg’ [float]**: the average scattering angle (i.e. between the optical axes of the illumination and detection); 180 corresponds to backscattering 
  - **‘Immersion\_medium’ [enum{other, air, water, oil}]**: the immersion medium used for the objective lens
  - **‘Objective\_model’ [string]** (optional): the description of the objective lens being used, including the manufacturer and magnification
  - **‘Temperature\_C’ [float]** (optional): the temperature measured as close as possible to the sample
  - **‘Temperature\_uncertainty\_C’ [float]** (optional)
  - **‘Datatime’ [string]** (optional): a [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) representation of the time when the experiment was started 
  - **‘Info’ [string]** (optional): any additional description that the user can input to describe the experiment
- **‘/Experiment\_info/** **Spectrometer\_ characterization’** (optional group) containing the dataset:
  - **IRF [float]** (optional): a 1D array containing the impulse response function of the spectrometer. It must have an attribute ‘Frequency\_GHz’ [float], of the same length, containing the frequency axis. 
- **‘/tn’** (group) containing the data of the current timepoint; it doesn’t need to be necessarily a timepoint in a timelapse, it could also be a measurement at different temperature or whatever fits under the concept of subsequent measurements. It can have any of the attributes defined in ‘Experiment\_info’ (if different); specifically, defining the ‘Datetime’ attribute is recommended. If the .Bh5 contains only a single timepoint, this group must still be defined and called ‘t0’
- **‘/tn/Analyzed\_data’** (group) containing the following datasets. All datasets must be 1D with the same length. The datasets containing the parameters extracted from the spectra (i.e. Shift\_n\_GHz, etc.) can have more dimensions, in order to match the dimensions in ‘Spectra/Amplitude’. Note that the word ‘dataset’ here is used in the way that it is defined by HDF5, not in an experimental sense; the way one should think about the group ‘Analyzed\_data’ is like a table containing a list of voxels acquired in the sample with their corresponding Brillouin shift, width, etc.
  - **‘Index’ [int]**: zero-based index to associate the current point to the spectral data
  - **‘Spatial\_position\_um’ [compound {x:float, y:float, z:float}]**: x,y,z coordinates in um on the sample
  - **‘Shift\_n\_GHz’ [float]**: n=0,… if multiple peaks are fitted
  - **‘Width\_n\_GHz’ [float]**: n=0,… if multiple peaks are fitted
  - **‘Amplitude\_n’ [float]**: n=0,… if multiple peaks are fitted
  - **‘Fit\_error\_n’ [compound {R2:float, RMSE:float}]** (optional)
  - **‘Calibration\_index’ [int]** (optional)**:** zero-based index (the idea being that, if multiple calibration spectra are acquired while imaging, we need to know which calibration data is used for the current spectrum)
  - **‘Timestamp\_ms’ [float]** (optional): milliseconds from the beginning of the experiment, as defined in the ‘datetime’ attribute of the current ‘tn’ group (if defined, or of the ‘/Experiment\_info’ otherwise) when the current spectrum was acquired
  - Additional optional datasets 
  
  
  It also contains the following attributes:
  - **‘Fit\_model’ [enum:{other, Lorentzian, DHO, Voigt}]**
  - **‘Corrections’ [string]**: text describing any corrections that is applied to the fitted data (e.g. for NA broadening, deconvolution, etc.)
- **‘/tn/Spectra’** (group) containing the spectra, which are used for fitting i.e. including all the processing of the raw data (e.g. linear interpolation, digital filter, etc.); the raw data (whose format can largely vary, depending on the microscope) can still be included in an additional dataset which might (or might not) be defined in a specific subtype of the .Bh5 file format. It must have the following datasets:
  - **‘Amplitude’ [float]**: 2D (or more) dataset where the first dimension corresponds to the indices in the ‘/Analyzed\_data/Index’ (and obviously has to have the same number of elements) and the second dimension contains the spectral information. Optionally can have more dimensions, when for each voxel in the sample multiple spectra are acquired (e.g. angle resolved measurements); the new dimensions must be inserted in-between (i.e. the “voxels” and spectral dimensions must always be the first and the last, to make the broadcast of the ‘Frequency’ dataset easier) 
  - **‘Parameters’ [float]** (optional): in case ‘Amplitude’ has more than 2 dimensions (let’s call the number of dimensions of ‘Amplitude’ n\_Amp), ‘Parameters’ must have n\_Amp-2 dimensions and contain the parameters at which the spectra were acquired (e.g. for an angle-resolved measurement the angle at which the spectrum was acquired). It must also have the following attributes:
    - **‘Name’ [string]**: a 1D array with size n\_Amp-2 containing the names of the parameters (e.g. ‘Angle’)
    - **‘Unit’ [string]**: a 1D array with size n\_Amp-2 containing the units of the parameters (e.g. ‘deg’) 
  - **‘Frequency’ [float]**: it must have the same size as ‘Amplitude’ or fewer dimensions; in the latter case it will be broadcasted to the size of ‘Amplitude’ (starting from the right), similarly to [Numpy broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html); e.g. if ‘Frequency’ is 1D  and ‘Amplitude’ is 2D, ‘Frequency’ must have the same length as the second dimension of ‘Amplitude’ (in this case the result of broadcasting is assuming that the frequency axis is the same for all the spatial positions). 

    It must have the attribute:
      - **‘Unit’ [string]**: specifying the unit (e.g. ‘GHz’, ‘px’) as a string; the possibility of having ‘px’ (or different unit) as a unit allows to accommodate cases when the calibration doesn’t provide absolute frequency (e.g. relative to the calibration material)
- **‘/tn/Images’** (optional group) containing the reconstructed images as 3D dataset in the format ZYX; the images must always have 3 dimensions, where the unused dimensions can be set to 1:
  - **‘Index’ [int]**: used to assign the specific pixel to the ‘Analysed\_data’ and ‘/Spectra/Amplitude’
  - **‘Shift\_n\_GHz’ [float]**
  - **‘Width\_n\_GHz’ [float]**
  - **‘Amplitude\_n’ [float]**
  - Optional additional channels specific of the modality in use (e.g. fit error, gain for stimulated, etc.) 
  
  To comply with definition of an [image object in HDF5](https://docs.hdfgroup.org/hdf5/v1_12/_i_m_g.html)) the datasets
  ‘Shift\_n\_GHz’, ‘Width\_n\_GHz’, etc. must have the following attributes:
  - **‘CLASS’ [string]**: "IMAGE"
  - **‘DISPLAY_ORIGIN’ [string]**: "UL"
  - **‘IMAGE_VERSION’ [string]**: "1.2" (the current version at the time of writing)
  - **‘element_size_um’ [float]**: array with 3 elements containing the pixel size (in um) for z, y, x; this is not required by HDF5 but it is used by FIJI to determine the pixel size
- **‘/tn/Calibration\_spectra’** (optional group) it contains the following datasets (N.B. if the n-th calibration data is the same as a previous timepoint, one can just use the attribute ‘same\_as’ without repeating the data):
  - **‘n’ [float]**: a 1D dataset containing the n-th calibration spectrum (where n is referring to ‘/Analyzed\_data/Calibration\_index’); in case there are multiple calibration materials (or reference frequency, e.g. in case of EOMs) the name of the dataset must be ‘n:m’, where m=0,… correspond to one material (frequency); it can optionally have an attribute **‘Timestamp\_ms’ [float]** corresponding to the milliseconds elapsed from ‘/tn/Calibration\_spectra/Datetime’

  It also contains the following attributes:
  - **‘same\_as’ [string]** (optional): to be used when the calibration data is the same as another ‘tn’; it contains the name of the group (e.g. ‘/t0’)
  - **‘Description’ [string]** (optional): it describes how the calibration is performed
  - **‘Temperature\_C’ [float]** (optional): the temperature of the calibration material (if relevant)
  - **‘Datatime’ [string]** (optional): a [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) representation of the time when the (first) calibration spectrum was acquired
  - **‘Shift\_m\_GHz’ [string]** (optional): Brillouin shift of the m-th calibration material (or frequency); the name must be ‘Shift\_0\_GHz’ in case a single material is used.
  - **‘FSR\_GHz’ [float]** (optional): The free spectral range of the spectrometer (in case it is a parameter that is used for calibration)
