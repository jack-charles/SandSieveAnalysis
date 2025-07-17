'''
@author: Jack Charles   https://jackcharlesconsulting.com/
'''

import math
import json
import numpy as np
import matplotlib.pyplot as plt
import util.wellengcalc as wec
import calcs.sand_analysis as saan

#initialize lists
srt_results:dict[str,saan.SandSieveData] = {}
selected_screens = []
selected_proppants = []
screen_database_filename = 'util/database_screen.json'
proppant_database_filename = 'util/database_proppant.json'
screen_dictionary = saan.import_screen_data(screen_database_filename)
proppant_dictionary = saan.import_proppant_data(proppant_database_filename)
sieve_unit = 'micron'
menu_loop = True

while menu_loop != False:
    print(f"\nCurrent Units are {sieve_unit}")
    print(f"Current Screens are {selected_screens}")
    print(f"Current Proppants are {selected_proppants}\n")
    menu_selection = int(input(f"Please type the number of selection\n"
                        "1: Open/Append Sand Sieve Data\n"
                        "2: Open Saved File\n"
                        "3: Import Screen Database\n"
                        "4: Import Proppant Database\n"
                        "5: Clear Sieve Data and Selected Data\n"
                        "6: Select Screen\n"
                        "7: Select Proppant\n"
                        "8: Select Units\n"
                        "10: Perform Calculations\n"
                        "11: Print SRT Data\n"
                        "12: Plot Results\n"
                        "20: Save File\n"
                        "0: Quit\n"
                        "Selection: "))

    if menu_selection == 1:
        sieve_data_filename = input("Path to Sand Sieve Data: ")
        try:
            srt_results.update(saan.import_sieve_data(sieve_data_filename))
        except FileNotFoundError:
            print("File not found")
    elif menu_selection == 2: 
        sieve_data_filename = input("Path to Saved File: ")
        try:
            sieve_unit, srt_results, selected_screens, selected_proppants = saan.read_saved_file_json(sieve_data_filename)
        except FileNotFoundError:
            print("File not found")
    elif menu_selection == 3:
        screen_database_filename = input("Path to Screen Database File: ")
        try:
            screen_dictionary = saan.import_screen_data(screen_database_filename)
        except FileNotFoundError:
            print("File not found")
    elif menu_selection == 4: 
        proppant_database_filename = input("Path to Proppant Database File: ")
        try:
            proppant_dictionary = saan.import_proppant_data(proppant_database_filename)
        except FileNotFoundError:
            print("File not found")
    elif menu_selection == 5: 
        selected_screens.clear()
        selected_proppants.clear()
        srt_results.clear()
        print("Sieve Data and Selections Cleared")
    elif menu_selection == 6:
        print(f"Available Screens: ",[f"{screen_dictionary[_x].name}" for _x in screen_dictionary],"\t")
        print(f"Screens Selected = {selected_screens}")
        selected_screens.append(input("Name of selected screen: "))
    elif menu_selection == 7: 
        print(f"Available Proppants: ",[f"{proppant_dictionary[_x]['name']}" for _x in proppant_dictionary],"\t")
        print(f"Proppants Selected = {selected_proppants}")
        selected_proppants.append(input("Name of selected proppant: "))
    elif menu_selection == 8:
        print("Available units are micron, mm, inch, phi, mesh")
        sieve_unit = input("Enter Sieve Units: ")
    elif menu_selection == 10:
        srt_results = saan.calculate_sieve_results(sieve_unit, srt_results, proppant_dictionary, selected_proppants[0])
        #only using the first proppant in list to perform Constein factor calculation
    elif menu_selection == 11:
        saan.print_sieve_analysis(srt_results)
    elif menu_selection == 12:
        saan.show_plots(srt_results, proppant_dictionary, screen_dictionary, selected_screens, selected_proppants)
    elif menu_selection == 20: 
        sieve_data_filename = input("Filename to Save To: ")
        saan.write_saved_file_json(sieve_unit, srt_results, selected_screens, selected_proppants, sieve_data_filename)
    elif menu_selection == 0:
        print("Thank you")
        menu_loop = False
    
    #Demo mode for testing
    elif menu_selection == 100:
        print("Demo Mode")
        screen_database_filename = 'util/database_screen.json'
        proppant_database_filename = 'util/database_proppant.json'
        sieve_data_filename = 'samples/sand_analysis_default_sievefile.txt'
        save_filename = 'samples/sand_analysis_default_sanddata.json'
        sieve_unit = 'micron'
        
        srt_results.update(saan.import_sieve_data(sieve_data_filename))
        screen_dictionary = saan.import_screen_data(screen_database_filename)
        #print(screen_dictionary)
        proppant_dictionary = saan.import_proppant_data(proppant_database_filename)
        #print(proppant_dictionary)
        selected_screens.append("6 Gauge WWS")
        selected_proppants.append("Gravel 20/40")
        selected_proppants.append("Carbolite 20/40")
        srt_results = saan.calculate_sieve_results(sieve_unit, srt_results, proppant_dictionary, selected_proppants[0])
        saan.write_saved_file_json(sieve_unit, srt_results, selected_screens, selected_proppants, save_filename)
        sieve_unit, srt_results, selected_screens, selected_proppants  = saan.read_saved_file_json('samples/sand_analysis_default_sanddata_new.json')
        #print_sieve_analysis(srt_results)
        samples = list(srt_results.keys())
        srt_results[samples[0]].print_sieve_results()
        saan.show_plots(srt_results, proppant_dictionary, screen_dictionary, selected_screens, selected_proppants)

    else:
        print("Invalid Selection")
