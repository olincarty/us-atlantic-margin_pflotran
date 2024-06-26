def gen_simulation_first(timesteps=10000):
    simulation = f"""
SIMULATION
  SIMULATION_TYPE SUBSURFACE
  PROCESS_MODELS
    SUBSURFACE_FLOW flow
      MODE HYDRATE
      OPTIONS
        NO_STATE_TRANSITION_OUTPUT
        #RESTRICT_STATE_CHANGE
        #USE_INFINITY_NORM_CONVERGENCE
        #MAX_PRESSURE_CHANGE 1.d5
        #MAX_TEMPERATURE_CHANGE 1.d0
        #FIX_UPWIND_DIRECTION
        #SAT_ABS_UPDATE_INF_TOL 1.d-6
        #SAT_REL_UPDATE_INF_TOL 1.d-8
      /
    /
  /
  CHECKPOINT
  /
END

SUBSURFACE
  NUMERICAL_METHODS flow
    TIMESTEPPER
      MAXIMUM_NUMBER_OF_TIMESTEPS {timesteps}
    /
    NEWTON_SOLVER
      USE_INFINITY_NORM_CONVERGENCE
      PRESSURE_CHANGE_LIMIT 1.d5
      TEMPERATURE_CHANGE_LIMIT 1.d0
      PRINT_LINEAR_ITERATIONS
/
END
"""
    return simulation


def gen_simulation_other(restart_name, timesteps=10000):
    simulation = f"""
SIMULATION
  SIMULATION_TYPE SUBSURFACE
  PROCESS_MODELS
    SUBSURFACE_FLOW flow
      MODE HYDRATE
      OPTIONS
        NO_STATE_TRANSITION_OUTPUT
        #RESTRICT_STATE_CHANGE
        #USE_INFINITY_NORM_CONVERGENCE
        #MAX_PRESSURE_CHANGE 1.d5
        #MAX_TEMPERATURE_CHANGE 1.d0
        #FIX_UPWIND_DIRECTION
        #SAT_ABS_UPDATE_INF_TOL 1.d-6
        #SAT_REL_UPDATE_INF_TOL 1.d-8
      /
    /
  /
  RESTART
    FILENAME {restart_name}
    RESET_TO_TIME_ZERO
  /
  CHECKPOINT
  /
END

SUBSURFACE
  NUMERICAL_METHODS flow
    TIMESTEPPER
      MAXIMUM_NUMBER_OF_TIMESTEPS {timesteps}
    /
    NEWTON_SOLVER
      USE_INFINITY_NORM_CONVERGENCE
      PRESSURE_CHANGE_LIMIT 1.d5
      TEMPERATURE_CHANGE_LIMIT 1.d0
/
END
"""
    return simulation


def gen_datasets(porosity_data='phi_k_dataset.h5', perm_data='perm_dataset.h5'):
    datasets = f"""
DATASET porosity
  FILENAME {porosity_data}
  HDF5_DATASET_NAME porosity
END
DATASET perm
  FILENAME {perm_data}
  HDF5_DATASET_NAME perm
END
"""
    return datasets


def gen_grid(sed_thick):
    grid = f"""
GRID
  TYPE STRUCTURED CARTESIAN
  NXYZ 1 1 {sed_thick}
  DXYZ
    1@1.d0
    1@1.d0
    {sed_thick}@1.d0
  /
 GRAVITY 0.d0 0.d0 -9.8d0
END
"""
    return grid


def gen_region(sed_thick):
    region = f"""
REGION all
  COORDINATES
    0.d0 0.d0 0.d0
    1.d0 1.d0 {sed_thick}.d0
  /
END

REGION top
  FACE TOP
  COORDINATES
    0.0d0 0.d0 {sed_thick}.d0
    1.0d0 1.d0 {sed_thick}.d0
  /
END

REGION bottom
  FACE BOTTOM
  COORDINATES
    0.d0 0.d0 0.d0
    1.d0 1.d0 0.d0
  /
END
"""
    return region


def gen_hydrate(org_carbon_frac, methanogenesis_rate, v_sed, smt_depth):
    hydrate = f"""
HYDRATE
  SCALE_PERM_BY_HYD_SAT
  EFFECTIVE_SAT_SCALING
  ADJUST_SOLUBILITY_WITHIN_GHSZ
  WITH_SEDIMENTATION
  WITH_GIBBS_THOMSON
  METHANOGENESIS
    NAME ss_methanogenesis
    ALPHA {org_carbon_frac}
    K_ALPHA 2241
    LAMBDA {methanogenesis_rate}
    V_SED {v_sed}
    SMT_DEPTH {smt_depth}
  /
  PERM_SCALING_FUNCTION DAI_AND_SEOL
END
"""
    return hydrate


def gen_fluid_prop():
    fluid_prop = f"""
FLUID_PROPERTY
  PHASE LIQUID
  DIFFUSION_COEFFICIENT 1.d-9
END

FLUID_PROPERTY
  PHASE GAS
  DIFFUSION_COEFFICIENT 2.d-5
END

EOS WATER
  # SURFACE_DENSITY 1024.0 kg/m^3
  # DENSITY IF97
  # DENSITY BATZLE_AND_WANG
  DENSITY CONSTANT 1024
  ENTHALPY IF97
  STEAM_DENSITY IF97
  STEAM_ENTHALPY IF97
  # VISCOSITY BATZLE_AND_WANG
END

EOS GAS
  DENSITY PR_METHANE
  ENTHALPY IDEAL_METHANE
  VISCOSITY DEFAULT #CONSTANT 1.1d-5 Pa-s #DEFAULT
END
"""
    return fluid_prop


def gen_mat_prop(therm_cond, permeability=1*10**-16.5):
    mat_prop = f"""
MATERIAL_PROPERTY clay
  ID 1
  CHARACTERISTIC_CURVES clay
  POROSITY DATASET porosity
  TORTUOSITY_FUNCTION_OF_POROSITY 1.4 #Van Loon and Mibus 2015
#  SOIL_COMPRESSIBILITY 1.6d-10 #1/Pa, Konikow and Neuzil 2007 REMOVED 11/26/2019
#  SOIL_COMPRESSIBILITY_FUNCTION LEIJNSE REMOVED 11/26/2019
#  SOIL_REFERENCE_PRESSURE 101325.d0 Reason why profiles were not working
  ROCK_DENSITY 2700.d0
  THERMAL_CONDUCTIVITY_DRY {therm_cond} W/m-C
  THERMAL_CONDUCTIVITY_WET {therm_cond} W/m-C
  HEAT_CAPACITY 830 J/kg-C
  PERMEABILITY
    DATASET perm
    # PERM_ISO {permeability}
    # PERM_ISO 1d-15
  /
  #SOIL_REFERENCE_PRESSURE INITIAL_PRESSURE
  #POROSITY_COMPRESSIBILITY 1.d-9
  #PORE_SIZE 250.d-9
  #SRL 0.1
  #SRG 1.0
END
"""
    return mat_prop


def gen_char_curves_vg():
    char_curves = """
CHARACTERISTIC_CURVES clay
  SATURATION_FUNCTION VAN_GENUCHTEN
    # ALPHA 5.8d-4  # first used
    # M 0.189  # first used
    ALPHA 6.851d-5  # actual value
    M 0.4559  # actual value
    # ALPHA 1.543763763883219d-6  # pf vg value
    # M 0.8276537863659102  # pf vg value
    LIQUID_RESIDUAL_SATURATION 0.1d0
    MAX_CAPILLARY_PRESSURE 1.d8 #roughly read from Jacinto et al. 2009
  /
  PERMEABILITY_FUNCTION MUALEM_VG_LIQ
    PHASE LIQUID
    # M 0.189  # first used
    M 0.4559  # actual value
    # M 0.8276537863659102  # pf vg value
    LIQUID_RESIDUAL_SATURATION 0.1d0
  /
  PERMEABILITY_FUNCTION MUALEM_VG_GAS
    PHASE GAS
    # M 0.189  # first used
    M 0.4559  # actual value
    # M 0.8276537863659102  # pf vg value
    LIQUID_RESIDUAL_SATURATION 0.1d0
    GAS_RESIDUAL_SATURATION 0.15d0
  /
END
"""
    return char_curves


def gen_char_curves():
    char_curves = """
CHARACTERISTIC_CURVES clay
  SATURATION_FUNCTION BROOKS_COREY
    LIQUID_RESIDUAL_SATURATION 0.010991454972825613
    ALPHA 9.097976587015271d-5
    LAMBDA 0.7803367014222499
    MAX_CAPILLARY_PRESSURE 1.d8 #roughly read from Jacinto et al. 2009
    SMOOTH
  /
  PERMEABILITY_FUNCTION MUALEM_BC_LIQ
    PHASE LIQUID
    LAMBDA 0.7803367014222499
    LIQUID_RESIDUAL_SATURATION 0.010991454972825613
  /
  PERMEABILITY_FUNCTION MUALEM_BC_GAS
    PHASE GAS
    LAMBDA 0.7803367014222499
    LIQUID_RESIDUAL_SATURATION 0.010991454972825613
    GAS_RESIDUAL_SATURATION 0.15d0
  /
END
"""
    return char_curves


def gen_strata():
    strata = f"""
STRATA
  REGION all
  MATERIAL clay
END
"""
    return strata


def gen_time(testTime):
    time = f"""
TIME
  FINAL_TIME {testTime} y
  INITIAL_TIMESTEP_SIZE 1.d-6 y
  MAXIMUM_TIMESTEP_SIZE 1.d4 y at 1.d6 y
END
"""
    return time


def gen_output(periodicTime):
    output = f"""
OUTPUT
  SNAPSHOT_FILE
    PERIODIC TIME {periodicTime} y
    # FORMAT HDF5
    FORMAT TECPLOT POINT
    NO_PRINT_INITIAL
  /
  #UNFILTER_NON_STATE_VARIABLES

  VARIABLES
    TEMPERATURE
    LIQUID_PRESSURE
    GAS_PRESSURE
    LIQUID_SATURATION
    GAS_SATURATION
    HYDRATE_SATURATION
    # ICE_SATURATION
    # LIQUID_MASS_FRACTIONS
    # LIQUID_MOLE_FRACTIONS
    # GAS_MASS_FRACTIONS
    LIQUID_DENSITY
    # LIQUID_DENSITY MOLAR
    GAS_DENSITY
    # GAS_DENSITY MOLAR
    PERMEABILITY
    # LIQUID_RELATIVE_PERMEABILITY
    # GAS_RELATIVE_PERMEABILITY
    POROSITY
  /
  
  SCREEN OFF
END
"""
    return output


def gen_flow_cond(sed_thick, geothermal_gradient, seafloor_pressure, seafloor_temperature,
                  sf_p_dct, sf_t_dct, heat_flux):
    nline_tab = '\n    '

    flow_cond = f"""
FLOW_CONDITION initial
  TYPE
    LIQUID_PRESSURE HYDROSTATIC
    MOLE_FRACTION DIRICHLET
    TEMPERATURE DIRICHLET
  /
  DATUM 0.d0 0.d0 {sed_thick}.d0
  GRADIENT
    TEMPERATURE 0.d0 0.d0 {geothermal_gradient}
  /
  LIQUID_PRESSURE {seafloor_pressure}
  MOLE_FRACTION 1.d-3
  TEMPERATURE {seafloor_temperature}
END

FLOW_CONDITION hyd_sat_initial
  TYPE
    LIQUID_PRESSURE HYDROSTATIC
    HYDRATE_SATURATION DIRICHLET
    TEMPERATURE DIRICHLET
  /
  DATUM 0.d0 0.d0 {sed_thick}.d0
  GRADIENT
    TEMPERATURE 0.d0 0.d0 {geothermal_gradient}
  /
  LIQUID_PRESSURE {seafloor_pressure}
  HYDRATE_SATURATION 1.d-8
  TEMPERATURE {seafloor_temperature}
END

FLOW_CONDITION top
  TYPE
    LIQUID_PRESSURE HYDROSTATIC
    MOLE_FRACTION DIRICHLET
    TEMPERATURE DIRICHLET
  /
  DATUM 0.d0 0.d0 {sed_thick}.d0
  GRADIENT
    TEMPERATURE 0.d0 0.d0 {geothermal_gradient}
  /
  # LIQUID_PRESSURE {seafloor_pressure}
  LIQUID_PRESSURE LIST
    TIME_UNITS y
    INTERPOLATION LINEAR
    # time # press
    {nline_tab.join(f"{key} {value}" for key, value in sf_p_dct.items())}
  /
  MOLE_FRACTION 0.d-3
  # TEMPERATURE {seafloor_temperature}
  TEMPERATURE LIST
    TIME_UNITS y
    INTERPOLATION LINEAR
    # time # temp
    {nline_tab.join(f"{key} {value}" for key, value in sf_t_dct.items())}
  /
END

FLOW_CONDITION bottom
  TYPE
    LIQUID_FLUX NEUMANN
    GAS_FLUX NEUMANN
    ENERGY_FLUX NEUMANN
  /
  LIQUID_FLUX {0} m/yr
  GAS_FLUX 0.d0
  ENERGY_FLUX {heat_flux} W/m^2
END
"""
    return flow_cond


def gen_init_cond():
    init_cond = f"""
# initial condition
INITIAL_CONDITION all
  FLOW_CONDITION initial
  REGION all
END

BOUNDARY_CONDITION top
  FLOW_CONDITION top
  REGION top
END

BOUNDARY_CONDITION bottom
  FLOW_CONDITION bottom
  REGION bottom
END
"""
    return init_cond
