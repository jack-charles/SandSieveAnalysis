'''
@author: Jack Charles   https://jackcharlesconsulting.com/
'''

import math
import json
import numpy as np
import matplotlib.pyplot as plt
import util.wellengcalc as wec

#units in microns. made as a dictionary for lookup
wentworth_sand_classification = {'Clay': 3.9, 'Silt': 62.0, 'VFG Sand': 125.0, 'FG Sand': 250.0, 'MG Sand': 500.0, 'CG Sand': 1000.0, 'VCG Sand': 2000.0, 'Gravel': 4000.0}
uniformity_classification = {'Highly Uniform': 3, 'Uniform': 5, 'Non-Uniform': 10, 'Highly Non-Uniform': 25}
mobile_fines_classification = {5: 'Fines Immobile', 10: 'Impairment Increasing', 25: 'Impairment Decreasing', 250: 'Fines Produced'}

class SandSieveData():
    def __init__(self, name:str, depth:float, sieve_sizes:list[float], retained:list[float], cumulative_wt_perc:list[float], 
                 d5:float, d10:float, d40:float, d50:float, d90:float, d95:float, uniformity_coeff:float, sorting_factor:float, 
                 effective_size:float, mobile_fines_coeff:float, mobile_fines_size:float, 
                 average_formation_pore:float, smallest_particle_to_bridge:float, largest_particle_thru_pore:float):
        self.name = name
        self.depth = depth
        self.sieve_sizes = sieve_sizes
        self.retained = retained
        self.cumulative_wt_perc = cumulative_wt_perc
        self.d5 = d5
        self.d10 = d10
        self.d40 = d40
        self.d50 = d50
        self.d90 = d90
        self.d95 = d95
        self.uniformity_coeff = uniformity_coeff
        self.sorting_factor = sorting_factor
        self.effective_size = effective_size
        self.mobile_fines_coeff = mobile_fines_coeff
        self.mobile_fines_size = mobile_fines_size
        self.average_formation_pore = average_formation_pore
        self.smallest_particle_to_bridge = smallest_particle_to_bridge
        self.largest_particle_thru_pore = largest_particle_thru_pore

    def calculate_sieve_parameters(self):
        _percentages = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95]
        self.depth = self.depth
        grain_size_percent = np.interp(_percentages, self.cumulative_wt_perc, self.sieve_sizes)
        self.d5 = grain_size_percent[0]
        self.d10 = grain_size_percent[1]
        self.d40 = grain_size_percent[4]
        self.d50 = grain_size_percent[5]
        self.d90 = grain_size_percent[9]
        self.d95 = grain_size_percent[10]
        self.uniformity_coeff = self.d40 / self.d90
        self.sorting_factor = self.d10 / self.d95
        self.effective_size = self.d50 / self.uniformity_coeff
        self.mobile_fines_coeff = self.d50/self.d95
        self.mobile_fines_size = self.d50 / 10
        self.average_formation_pore = self.d50 / 6.5          #or 6 - use a variable in next iteration
        self.smallest_particle_to_bridge = self.average_formation_pore / 3
        self.largest_particle_thru_pore = self.average_formation_pore / 7
        self.recommended_gravel_D50 = self.d50 * 6
        self.recommended_frac_D50 = self.d50 * 8              #or 10 - use a variable in next iteration

    def calculate_constien_criteria(self, proppant_pack_pore_size:float):
        self.constien_criteria = self.d50 / self.uniformity_coeff / proppant_pack_pore_size

    def convert_sieve_sizes(self, sieve_unit):      #convert all to microns
        if sieve_unit == 'micron':
            self.sieve_sizes = [1 * _sizes for _sizes in self.sieve_sizes]
        elif sieve_unit == 'mm':
            self.sieve_sizes = [1000 * _sizes for _sizes in self.sieve_sizes]
        elif sieve_unit == 'in':
            self.sieve_sizes = [25.4 * _sizes for _sizes in self.sieve_sizes]
        elif sieve_unit == 'phi':
            self.sieve_sizes = [1000 * 2 ** -(_sizes) for _sizes in self.sieve_sizes]
        elif sieve_unit == 'mesh':
            self.sieve_sizes = [1 * _sizes for _sizes in self.sieve_sizes] #TO FIX

    def print_sieve_results(self):
        print(self.name,"\t",self.depth,"\t",[f"{_x:.2f}" for _x in self.retained],"\t",[f"{_y:.2f}" for _y in self.cumulative_wt_perc])
        print(f"{self.name}\t{self.depth}\td10={self.d10:.2f}\td50={self.d50:.2f}\tUniformity={self.uniformity_coeff:.2f}\tSorting={self.sorting_factor:.2f}")

class ScreenData():
    def __init__(self, name:str, type:str, aperture:float):
        self.name = name
        self.type = type
        self.aperture = aperture

class ProppantData():
    def __init__(self, name:str, permeability:float, abs_density:float, abs_volume:float, bulk_density:float, D50:float):
        self.name = name
        self.permeability = permeability
        self.abs_density = abs_density
        self.abs_volume = abs_volume
        self.bulk_density = bulk_density
        self.D50 = D50

    def calculate_proppant_parameters(self):
        self.proppant_pack_pore_size = self.D50 / 6.5                      #or 6 - use a variable in next iteration
        self.smallest_particle_to_bridge = self.proppant_pack_pore_size / 3
        self.largest_particle_thru_pore = self.proppant_pack_pore_size / 7

def read_saved_file_json(data_filename:str):
    with open(data_filename, 'r',) as file:
        data_dictionary = json.load(file)
    sieve_data:dict[str,SandSieveData] = {}
    _dd = data_dictionary['SRT Results']
    for key in _dd:
        sieve_data[key] = SandSieveData(_dd[key]['Name'], _dd[key]['Depth'], _dd[key]['Sieve Sizes'], 
                                        _dd[key]['Retained Weight'], _dd[key]['Cumulative Weight Percentage'],
                                        _dd[key]['d5'], _dd[key]['d10'], _dd[key]['d40'], 
                                        _dd[key]['d50'], _dd[key]['d90'], _dd[key]['d95'],
                                        _dd[key]['UC'], _dd[key]['Sorting'], _dd[key]['Effective Size'], 
                                        _dd[key]['Mobile Fines Coefficient'], _dd[key]['Mobile Fines Size'], 
                                        _dd[key]['Average Formation Pore Size'], _dd[key]['Smallest Particle to Bridge'], 
                                        _dd[key]['Largest Particle to Pass Through'])
    unit = data_dictionary['Sieve Units']
    selected_screens = data_dictionary['Selected Screen']
    selected_proppants = data_dictionary['Selected Proppant']
    return unit, sieve_data, selected_screens, selected_proppants

def write_saved_file_json(unit, sieve_data:dict[str,SandSieveData], selected_screen:list, selected_proppant:list, data_filename:str):
    data_dictionary = {}
    data_dictionary['Sieve Units'] = unit
    data_dictionary['Selected Screen'] = selected_screen
    data_dictionary['Selected Proppant'] = selected_proppant
    data_dictionary['SRT Results'] = {}
    for i in sieve_data.keys():
        data_dictionary['SRT Results'][i] = {'Name':sieve_data[i].name, 'Depth':sieve_data[i].depth, 'Sieve Sizes':sieve_data[i].sieve_sizes, 
                            'Retained Weight':sieve_data[i].retained, 'Cumulative Weight Percentage':sieve_data[i].cumulative_wt_perc,
                            'd5':sieve_data[i].d5, 'd10':sieve_data[i].d10, 'd40':sieve_data[i].d40, 'd50':sieve_data[i].d50, 'd90':sieve_data[i].d90, 'd95':sieve_data[i].d95,
                            'UC':sieve_data[i].uniformity_coeff, 'Sorting':sieve_data[i].sorting_factor, 'Effective Size':sieve_data[i].effective_size,
                            'Mobile Fines Coefficient':sieve_data[i].mobile_fines_coeff, 'Mobile Fines Size':sieve_data[i].mobile_fines_size,
                            'Average Formation Pore Size':sieve_data[i].average_formation_pore, 'Smallest Particle to Bridge':sieve_data[i].smallest_particle_to_bridge,
                            'Largest Particle to Pass Through':sieve_data[i].largest_particle_thru_pore}
    with open(data_filename, 'w',) as file:
        json.dump(data_dictionary, file)

def import_sieve_data(data_filename:str):
    sieve_data_ndarray = np.genfromtxt(data_filename, delimiter=',', dtype=None, names=True, autostrip=False, deletechars="~!@#$%^&*()-=+~|]}[{';: ?>,<")  
    _x = []
    sieve_data:dict[str,SandSieveData] = {}
    for sieve_data_content in sieve_data_ndarray:
        _x = sieve_data_content.tolist()
        #name, depth, sieve sizes from header names in ndarray, wt retained
        sieve_data[_x[0]] = SandSieveData(_x[0], float(_x[1]), [float(_y) for _y in sieve_data_ndarray.dtype.names[2:]], list(_x[2:]), [], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    return sieve_data

def import_screen_data(data_filename:str):
    with open(data_filename, 'r',) as file:
        data_dictionary = json.load(file)
    screen_dictionary:dict = {}
    _dd = data_dictionary
    for key in _dd:
        screen_dictionary[key] = {'name': _dd[key]['name'], 'type': _dd[key]['type'], 'aperture_micron': _dd[key]['aperture_micron']}
    return screen_dictionary

def import_proppant_data(data_filename:str):    
    with open(data_filename, 'r',) as file:
        data_dictionary = json.load(file)
    #unit_class = UnitSystemClass(**json_data)      #assign to a class object if keys match objects
    proppant_dictionary:dict = {}
    _dd = data_dictionary
    for key in _dd:
        proppant_dictionary[key] = {'name': _dd[key]['name'], 'permeability_D': _dd[key]['permeability_D'], 'density_SG': _dd[key]['density_SG'], 'absvol_gal/lb': _dd[key]['absvol_gal/lb'], 'bulk_density_lb/ft3': _dd[key]['bulk_density_lb/ft3'], 'D50_micron': _dd[key]['D50_micron']}
    #data_ndarray = np.genfromtxt(filename, delimiter=',', dtype='|U40, float, float, float, float, float', names=True, autostrip=True)
    #data_class, _x, proppant_dictionary = [], [], {}
    #for data_content in data_ndarray:
    #    _x = data_content.tolist()
    #    data_class.append(ProppantData(_x[0], _x[1], _x[2], _x[3], _x[4], _x[5]))
    #convert to dictionary for simple selection of data
    #for _x in range(len(data_class)):
    #    data_class[_x].calculate_proppant_parameters()
    #    proppant_dictionary[data_class[_x].name] = data_class[_x] 
    return proppant_dictionary

def calculate_sieve_results(unit, sieve_data:dict[str,SandSieveData], proppant_dictionary:dict, selected_proppant:list[str]):
    for _x in sieve_data.keys():
        sieve_data[_x].cumulative_wt_perc = []
        sieve_data[_x].convert_sieve_sizes(unit)
        for _y in range(len(sieve_data[_x].retained)):
            sieve_data[_x].cumulative_wt_perc.append(100 * sum(sieve_data[_x].retained[:_y+1]) / sum(sieve_data[_x].retained))     #y+1 is needed y is the length of the range, and we need 1 after the length for slicer
        sieve_data[_x].calculate_sieve_parameters()
        try:
            sieve_data[_x].calculate_constien_criteria(proppant_dictionary[selected_proppant]['D50_micron']/6.5)
        except:
            sieve_data[_x].constien_criteria = 0
    return sieve_data

def print_sieve_data(sieve_data):
    keys = list(sieve_data.keys())
    print(f"Name\tDepth\t{sieve_data[keys[0]].sieve_sizes}")
    for _x in sieve_data.keys():
        print(sieve_data[_x].name,"\t",sieve_data[_x].depth,"\t",
              [f"{_retained:.2f}" for _retained in sieve_data[_x].retained])

def print_sieve_analysis(sieve_data):
    print(f"Name\tDepth\tD50\tUniformity")
    for _x in sieve_data.keys():
        print(f"{sieve_data[_x].name}\t{sieve_data[_x].depth:.2f}\t",
                f"{sieve_data[_x].d50:.2f}\t{sieve_data[_x].uniformity_coeff:.2f}")

def show_plots(srt_results:dict[str,SandSieveData], proppant_dictionary:dict, screen_dictionary:dict, selected_screens:list, selected_proppants:list):
    #plots
    fig, ax1 = plt.subplots(2,4)
    fig.suptitle("Grain Size Distribution and Uniformity Coefficients")
    fig.tight_layout()
    #plt.rcParams['axes.labelsize'] = 8
    samples = list(srt_results.keys())
    for sample in samples:
            ax1[0, 0].plot(srt_results[sample].sieve_sizes, srt_results[sample].retained, label=srt_results[sample].name)
            ax1[1, 0].plot(srt_results[sample].sieve_sizes, srt_results[sample].cumulative_wt_perc)
            ax1[0, 1].plot(srt_results[sample].uniformity_coeff, srt_results[sample].depth, marker='o', linestyle='None')
            ax1[1, 1].plot(srt_results[sample].uniformity_coeff, srt_results[sample].d50,  marker='o', linestyle='None')
            ax1[0, 3].plot(srt_results[sample].d10, srt_results[sample].depth, marker='o', linestyle='None')
            ax1[1, 3].plot(6*srt_results[sample].d50, srt_results[sample].depth, marker='o', linestyle='None')
    
    #ax1[0, 0].plot([SandSieveData.sieve_sizes for SandSieveData in srt_results], [SandSieveData.sieve_sizes for SandSieveData in srt_results])

    #ax1[0, 0].plot([srt_results[key].sieve_sizes for key in srt_results.keys()], 
    #            [srt_results[key].retained for key in srt_results.keys()], label=srt_results[sample].name)

    ax1[0, 2].plot([srt_results[key].average_formation_pore for key in srt_results.keys()], 
                [srt_results[key].depth for key in srt_results.keys()], label="Average Formation Pore Size")
    ax1[0, 2].plot([srt_results[key].mobile_fines_size for key in srt_results.keys()], 
                [srt_results[key].depth for key in srt_results.keys()], label="Mobile Fines Size")
    ax1[0, 2].plot([srt_results[key].smallest_particle_to_bridge for key in srt_results.keys()], 
                [srt_results[key].depth for key in srt_results.keys()], label="Smallest Particle to Bridge")
    ax1[0, 2].plot([srt_results[key].largest_particle_thru_pore for key in srt_results.keys()], 
                [srt_results[key].depth for key in srt_results.keys()], label="Largest Particle to Pass Thru Avg Pore")
    ax1[0, 2].plot([srt_results[key].mobile_fines_coeff for key in srt_results.keys()], 
                [srt_results[key].depth for key in srt_results.keys()], label="Mobile Fines Coeff", marker='o', linestyle='None')
    
    #temporary variable to store proppant D50 for plotting
    _proppantD50 = []
    for proppant in selected_proppants:
        _proppantD50.append(proppant_dictionary[proppant]['D50_micron'])
    for sample in srt_results.keys():
        ax1[1, 2].plot(selected_proppants, [_x/srt_results[sample].d50 for _x in _proppantD50], marker='o', linestyle='None')  

    ax1[0, 0].set_xlabel("Grain Size")
    ax1[0, 0].xaxis.set_inverted(True)
    ax1[0, 0].set_xscale('log')
    ax1[0, 0].set_ylabel("Weight retained")
    ax1[0, 0].yaxis.tick_right()
    ax1[0, 0].set_yticks(np.arange(0,11,1))
    ax1[0, 0].yaxis.set_label_position('right')
    ax1[0, 0].grid(True)
    ax1[0, 0].legend(loc='best', fontsize=8)
    for _key in wentworth_sand_classification:
        ax1[0, 0].axvline(x = wentworth_sand_classification[_key], color='gray', linestyle='dashed')
        ax1[0, 0].annotate(xy = (wentworth_sand_classification[_key], srt_results[samples[0]].depth), text=_key, 
                        horizontalalignment='left', verticalalignment='top', fontsize=6, rotation=90)

    ax1[1, 0].set_xlabel("Grain Size")
    ax1[1, 0].xaxis.set_inverted(True)
    ax1[1, 0].set_xscale('log')
    ax1[1, 0].set_ylabel("Cumulative Weight retained")
    ax1[1, 0].yaxis.tick_right()
    ax1[1, 0].set_yticks(np.arange(0,110,10))
    ax1[1, 0].yaxis.set_label_position('right')
    ax1[1, 0].grid(True)
    for _key in wentworth_sand_classification:
        ax1[1, 0].axvline(x = wentworth_sand_classification[_key], color='gray', linestyle='dashed')
        ax1[1, 0].annotate(xy = (wentworth_sand_classification[_key], 100), text = _key, 
                        horizontalalignment = 'left', verticalalignment = 'top', fontsize = 6, rotation = 90)

    ax1[0, 1].set_xlabel("Uniformity Coefficient")
    ax1[0, 1].set_ylabel("Depth")
    ax1[0, 1].yaxis.set_inverted(True)
    ax1[0, 1].grid(True)
    for _key in uniformity_classification:
        ax1[0, 1].axvline(x = uniformity_classification[_key], color='gray', linestyle='dashed')
        ax1[0, 1].annotate(xy = (uniformity_classification[_key], srt_results[samples[0]].depth), text = _key, 
                          horizontalalignment = 'right', verticalalignment = 'top', fontsize = 6, rotation = 90)

    ax1[1, 1].set_xlabel("Uniformity Coefficient")
    ax1[1, 1].set_ylabel("d50")
    ax1[1, 1].grid(True)
    for _key in uniformity_classification:
        ax1[1, 1].axvline(x = uniformity_classification[_key], color='gray', linestyle='dashed')
        ax1[1, 1].annotate(xy = (uniformity_classification[_key], 100), text = _key, 
                          horizontalalignment = 'right', verticalalignment = 'top', fontsize = 6, rotation = 90)

    ax1[0, 2].set_xlabel("Grain & Pore Size")
    ax1[0, 2].set_ylabel("Depth")
    ax1[0, 2].yaxis.set_inverted(True)
    ax1[0, 2].grid(True)
    ax1[0, 2].legend(loc='best', fontsize=6)

    ax1[1, 2].set_xlabel("Proppant", fontsize=8)
    ax1[1, 2].set_ylabel("D50/d50", fontsize=8)
    ax1[1, 2].tick_params(axis='x', labelsize=6, rotation=90)
    ax1[1, 2].grid(True)
    for ratios in [6, 8, 10]:
        ax1[1, 2].axhline(y = ratios, color='red', linestyle='-')

    ax1[0, 3].set_xlabel("d10 and Screen Size")
    ax1[0, 3].set_ylabel("Depth")
    ax1[0, 3].yaxis.set_inverted(True)
    ax1[0, 3].grid(True)
    for _screen in selected_screens:
        ax1[0, 3].axvline(x = screen_dictionary[_screen]['aperture_micron'], color='red', linestyle="-")
        ax1[0, 3].annotate(xy = (screen_dictionary[_screen]['aperture_micron'], srt_results[samples[0]].depth), text = screen_dictionary[_screen]['name'], 
                        horizontalalignment = 'right', verticalalignment = 'top', fontsize = 8, rotation = 90)

    ax1[1, 3].set_xlabel("6d50 and Gravel D50")
    ax1[1, 3].set_ylabel("Depth")
    ax1[1, 3].yaxis.set_inverted(True)
    ax1[1, 3].grid(True)
    for proppant in selected_proppants:
        ax1[1, 3].axvline(x = proppant_dictionary[proppant]['D50_micron'], color='red', linestyle='-')
        ax1[1, 3].annotate(xy = (proppant_dictionary[proppant]['D50_micron'], srt_results[samples[0]].depth), text = proppant_dictionary[proppant]['name'], 
                        horizontalalignment = 'right', verticalalignment = 'top', fontsize = 8, rotation = 90)   

    plt.show()


