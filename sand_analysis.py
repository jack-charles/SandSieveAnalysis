"""
@author: Jack Charles   jack@jackcharlesconsulting.com
"""






import math
import json
import numpy as np
import matplotlib.pyplot as plt
import wellengcalc as wec

#units in microns. made as a dictionary for lookup
wentworth_sand_classification = {'Clay': 3.9, 'Silt': 62.0, 'VFG Sand': 125.0, 'FG Sand': 250.0, 
                               'MG Sand': 500.0, 'CG Sand': 1000.0, 'VCG Sand': 2000.0, 'Gravel': 4000.0}
uniformity_classification = {3: 'Highly Uniform', 5: 'Uniform', 10: 'Non-Uniform', 25: 'Highly Non-Uniform'}
mobile_fines_classification = {5: 'Fines Immobile', 10: 'Impairment Increasing', 25: 'Impairment Decreasing', 250: 'Fines Produced'}


class SandSieveClass():
    def __init__(self, name, depth, sieve_sizes, retained, cumulative_wt_perc, 
                 d5, d10, d40, d50, d90, d95, uniformity_coeff, sorting_factor, 
                 effective_size, mobile_fines_coeff, mobile_fines_size, 
                 average_formation_pore, smallest_particle_to_bridge, largest_particle_thru_pore):
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

    def calculate_constien_criteria(self, proppant_pack_pore_size):
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
            self.sieve_sizes = [1 * _sizes for _sizes in self.sieve_sizes]

    def print_sieve_results(self):
        print(self.name,"\t",self.depth,"\t",[f"{_x:.2f}" for _x in self.retained],"\t",[f"{_y:.2f}" for _y in self.cumulative_wt_perc])
        print(f"{self.name}\t{self.depth}\td10={self.d10:.2f}\td50={self.d50:.2f}\tUniformity={self.uniformity_coeff:.2f}\tSorting={self.sorting_factor:.2f}")

class ScreenDataClass():
    def __init__(self, name, type, aperture):
        self.name = name
        self.type = type
        self.aperture = aperture

class ProppantDataClass():
    def __init__(self, name, permeability, abs_density, abs_volume, bulk_density, D50):
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

def read_sieve_data_file(data_filename):
    data_ndarray = np.genfromtxt(data_filename, delimiter=',', dtype=None, names=True, autostrip=False, deletechars="~!@#$%^&*()-=+~|]}[{';: ?>,<")  
    data_class, _x, = [], []
    for data_content in data_ndarray:
        _x = data_content.tolist()
        data_class.append(SandSieveClass(_x[0], float(_x[1]), [float(_y) for _y in data_ndarray.dtype.names[2:]], list(_x[2:]), [], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    return data_class

def read_saved_file_json(data_filename):
    with open(data_filename, 'r',) as file:
        filedata = json.load(file)
    data_list = []
    for key in filedata['SRT Results']:
        data_list.append(SandSieveClass(filedata['SRT Results'][key]['Name'], filedata['SRT Results'][key]['Depth'], filedata['SRT Results'][key]['Sieve Sizes'], 
                                       filedata['SRT Results'][key]['Retained Weight'], filedata['SRT Results'][key]['Cumulative Weight Percentage'],
                                       filedata['SRT Results'][key]['d5'], filedata['SRT Results'][key]['d10'], filedata['SRT Results'][key]['d40'], 
                                       filedata['SRT Results'][key]['d50'], filedata['SRT Results'][key]['d90'], filedata['SRT Results'][key]['d95'],
                                       filedata['SRT Results'][key]['UC'], filedata['SRT Results'][key]['Sorting'], filedata['SRT Results'][key]['Effective Size'], 
                                       filedata['SRT Results'][key]['Mobile Fines Coefficient'], filedata['SRT Results'][key]['Mobile Fines Size'], 
                                       filedata['SRT Results'][key]['Average Formation Pore Size'], filedata['SRT Results'][key]['Smallest Particle to Bridge'], 
                                       filedata['SRT Results'][key]['Largest Particle to Pass Through']))
    unit = filedata['Sieve Units']
    selected_screens = filedata['Selected Screen']
    selected_proppants = filedata['Selected Proppant']
    return unit, data_list, selected_screens, selected_proppants

def read_saved_file_sql():  #to do
    return

def append_sieve_data(data, data_filename):
    new_data = read_sieve_data_file(data_filename)
    data.extend(new_data)

def read_screen_data_file(data_filename):    
    data_ndarray = np.genfromtxt(data_filename, delimiter=',', dtype='|U40, |U40, float', names=True, autostrip=True)
    data_class, _x, screen_dictionary = [], [], {}
    for data_content in data_ndarray:
        _x = data_content.tolist()
        data_class.append(ScreenDataClass(_x[0], _x[1], _x[2]))
    #convert to dictionary for simple selection of data
    for _x in range(len(data_class)):
        screen_dictionary[data_class[_x].name] = data_class[_x]  
    return screen_dictionary

def read_proppant_data_file(data_filename):    
    data_ndarray = np.genfromtxt(data_filename, delimiter=',', dtype='|U40, float, float, float, float, float', names=True, autostrip=True)
    data_class, _x, proppant_dictionary = [], [], {}
    for data_content in data_ndarray:
        _x = data_content.tolist()
        data_class.append(ProppantDataClass(_x[0], _x[1], _x[2], _x[3], _x[4], _x[5]))
    #convert to dictionary for simple selection of data
    for _x in range(len(data_class)):
        data_class[_x].calculate_proppant_parameters()
        proppant_dictionary[data_class[_x].name] = data_class[_x] 
    return proppant_dictionary

def calculate_sieve_results(unit, data_class, proppant_dictionary, selected_proppant):
    for _x in range(len(data_class)):
        data_class[_x].cumulative_wt_perc = []
        data_class[_x].convert_sieve_sizes(unit)
        for _y in range(len(data_class[_x].retained)):
            data_class[_x].cumulative_wt_perc.append(100 * sum(data_class[_x].retained[:_y+1]) / sum(data_class[_x].retained))     #y+1 is needed y is the length of the range, and we need 1 after the length for slicer
        data_class[_x].calculate_sieve_parameters()
        data_class[_x].calculate_constien_criteria(proppant_dictionary[selected_proppant].proppant_pack_pore_size)
    return data_class

def write_sieve_data_json(unit, datalist, data_filename = 'sanddata.json'):
    datadictionary = {}
    srtdictionary = {}
    datadictionary['Sieve Units'] = unit
    for i in range(len(datalist)):
        srtdictionary["Sample "+str(i)] = {'Name':datalist[i].name, 'Depth':datalist[i].depth, 'Sieve Sizes':datalist[i].sieve_sizes, 
                                            'Retained Weight':datalist[i].retained,                                           
                                            }
    with open(data_filename, 'w',) as file:
        json.dump(datadictionary, file)
    return

def write_sieve_data_sql():
    return

def export_sieve_results_file(unit, datalist, selected_screen_list, selected_proppant_list, data_filename = 'sanddataexport.json'):
    datadictionary = {}
    srtdictionary = {}
    datadictionary['Sieve Units'] = unit
    datadictionary['Selected Screen'] = selected_screen_list
    datadictionary['Selected Proppant'] = selected_proppant_list
    for i in range(len(datalist)):
        srtdictionary["Sample "+str(i)] = {'Name':datalist[i].name, 'Depth':datalist[i].depth, 'Sieve Sizes':datalist[i].sieve_sizes, 
                                            'Retained Weight':datalist[i].retained, 'Cumulative Weight Percentage':datalist[i].cumulative_wt_perc,
                                            'd5':datalist[i].d5, 'd10':datalist[i].d10, 'd40':datalist[i].d40, 'd50':datalist[i].d50, 'd90':datalist[i].d90, 'd95':datalist[i].d95,
                                            'UC':datalist[i].uniformity_coeff, 'Sorting':datalist[i].sorting_factor, 'Effective Size':datalist[i].effective_size,
                                            'Mobile Fines Coefficient':datalist[i].mobile_fines_coeff, 'Mobile Fines Size':datalist[i].mobile_fines_size,
                                            'Average Formation Pore Size':datalist[i].average_formation_pore, 'Smallest Particle to Bridge':datalist[i].smallest_particle_to_bridge,
                                            'Largest Particle to Pass Through':datalist[i].largest_particle_thru_pore,                                          
                                            }
    datadictionary['SRT Results'] = srtdictionary
    with open(data_filename, 'w',) as file:
        json.dump(datadictionary, file)

def print_sieve_data(sand_sieve_data_list):
    print(f"Name\tDepth\t{sand_sieve_data_list[0].sieve_sizes}")
    for _x in range(len(sand_sieve_data_list)):
        print(sand_sieve_data_list[_x].name,"\t",sand_sieve_data_list[_x].depth,"\t",
              [f"{_retained:.2f}" for _retained in sand_sieve_data_list[_x].retained])

def print_sieve_analysis(sand_sieve_data_list):
    print(f"Name\tDepth\tD50\tUniformity")
    for _x in range(len(sand_sieve_data_list)):
        print(f"{sand_sieve_data_list[_x].name}\t{sand_sieve_data_list[_x].depth:.2f}\t",
                f"{sand_sieve_data_list[_x].d50:.2f}\t{sand_sieve_data_list[_x].uniformity_coeff:.2f}")

def show_plots(srt_results, proppant_dictionary, screen_dictionary, selected_screens, selected_proppants):
    #plots
    fig, ax1 = plt.subplots(2,4)
    fig.suptitle("Grain Size Distribution and Uniformity Coefficients")
    fig.tight_layout()
    #plt.rcParams['axes.labelsize'] = 8
    
    for sample in range(len(srt_results)):
            ax1[0, 0].plot(srt_results[sample].sieve_sizes, srt_results[sample].retained, label=srt_results[sample].name)
            #ax1[0, 0].plot(srt_results[sample].sieve_sizes, srt_results[sample].cumulative_wt_perc)
            ax1[1, 0].plot(srt_results[sample].sieve_sizes, srt_results[sample].cumulative_wt_perc)
            ax1[0, 1].plot(srt_results[sample].uniformity_coeff, srt_results[sample].depth, marker='o', linestyle='None')
            ax1[1, 1].plot(srt_results[sample].uniformity_coeff, srt_results[sample].d50,  marker='o', linestyle='None')
            ax1[0, 3].plot(srt_results[sample].d10, srt_results[sample].depth, marker='o', linestyle='None')
            ax1[1, 3].plot(6*srt_results[sample].d50, srt_results[sample].depth, marker='o', linestyle='None')

    ax1[0, 2].plot([SandSieveClass.average_formation_pore for SandSieveClass in srt_results], 
                [SandSieveClass.depth for SandSieveClass in srt_results], label="Average Formation Pore Size")
    ax1[0, 2].plot([SandSieveClass.mobile_fines_size for SandSieveClass in srt_results], 
                [SandSieveClass.depth for SandSieveClass in srt_results], label="Mobile Fines Size")
    ax1[0, 2].plot([SandSieveClass.smallest_particle_to_bridge for SandSieveClass in srt_results], 
                [SandSieveClass.depth for SandSieveClass in srt_results], label="Smallest Particle to Bridge")
    ax1[0, 2].plot([SandSieveClass.largest_particle_thru_pore for SandSieveClass in srt_results], 
                [SandSieveClass.depth for SandSieveClass in srt_results], label="Largest Particle to Pass Thru Avg Pore")
    ax1[0, 2].plot([SandSieveClass.mobile_fines_coeff for SandSieveClass in srt_results], 
                [SandSieveClass.depth for SandSieveClass in srt_results], label="Mobile Fines Coeff", marker='o', linestyle='None')
    
    #temporary variable to store proppant D50 for plotting
    _proppantD50 = []
    for proppant in selected_proppants:
        _proppantD50.append(proppant_dictionary[proppant].D50)
    for sample in range(len(srt_results)):
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
        ax1[0, 0].annotate(xy = (wentworth_sand_classification[_key], srt_results[1].depth), text=_key, 
                        horizontalalignment='left', verticalalignment='bottom', fontsize=6, rotation=90)

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
        ax1[0, 1].axvline(x = _key, color='gray', linestyle='dashed')
        ax1[0, 1].annotate(xy = (_key, 100), text = uniformity_classification[_key], 
                          horizontalalignment = 'right', verticalalignment = 'top', fontsize = 6, rotation = 90)

    ax1[1, 1].set_xlabel("Uniformity Coefficient")
    ax1[1, 1].set_ylabel("d50")
    ax1[1, 1].grid(True)
    for _key in uniformity_classification:
        ax1[1, 1].axvline(x = _key, color='gray', linestyle='dashed')
        ax1[1, 1].annotate(xy = (_key, 100), text = uniformity_classification[_key], 
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
        ax1[0, 3].axvline(x = screen_dictionary[_screen].aperture, color='red', linestyle="-")
        ax1[0, 3].annotate(xy = (screen_dictionary[_screen].aperture, srt_results[1].depth), text = screen_dictionary[_screen].name, 
                        horizontalalignment = 'right', verticalalignment = 'top', fontsize = 8, rotation = 90)

    ax1[1, 3].set_xlabel("6d50 and Gravel D50")
    ax1[1, 3].set_ylabel("Depth")
    ax1[1, 3].yaxis.set_inverted(True)
    ax1[1, 3].grid(True)
    for proppant in selected_proppants:
        ax1[1, 3].axvline(x = proppant_dictionary[proppant].D50, color='red', linestyle='-')
        ax1[1, 3].annotate(xy = (proppant_dictionary[proppant].D50, srt_results[1].depth), text = proppant_dictionary[proppant].name, 
                        horizontalalignment = 'right', verticalalignment = 'top', fontsize = 8, rotation = 90)   

    plt.show()


