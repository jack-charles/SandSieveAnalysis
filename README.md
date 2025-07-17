# SandSieveAnalysis
Sand Sieve Analysis for sand control design

This is a script to interpret results from a sand sieve test, calculating the cumulative weight percentages, various size and sorting factors, and allow plotting of results with selected screens and proppants.

Please check the paths in the imports to use this application.

For a quick demo mode, enter 100 at the menu to read the default data and provide graphs.

Description of options and recommended order

<img width="412" height="276" alt="sand_analysis input" src="https://github.com/user-attachments/assets/2369b4b8-1d0a-4a13-80b5-0dae48496cb6" />


At the top the current unit system, and selected screens and proppants to evaluate are listed for reference. These may be changed in the options.

1 - Open/Append Sand Sieve Data. This will be a typical sand sieve analysis file of weight retained per mesh size. File format is Name of sample, Depth, and weight retained on a mesh size. Mesh sizes must be the same for all entries per uploaded files, however upon assignment the mesh sizes will be stored for each sample. This option may be used to append multiple sieve data sets together, including if a different set of meshes were used for the data set.

2 - Open Saved File. The program will ultimately create a JSON file that will save the sand sieve data and all calculations performed with it. Each entry will have it's own set of mesh sizes with it, so this JSON can accommodate samples that were done with different meshes, say if you had old data from a different sieve shaker that you wanted to compare new results with.

3 - Import Screen Database. Import screen name, type, and aperture (slot width or pore size), and assigns to a dictionary. The default_screendatabase.txt will be loaded by default, and may be changed.

4 - Import Proppant Database. Imports proppant name, permeability, specific gravity, absolute volume, bulk density, and D50, and assigns to a dictionary. This data is usually provided by the manufacturer. For best results, use permeability that is based on the confining stresses that will be observed. The default_proppantdatabase.txt will be loaded by default, and may be changed.

5 - Clear Sieve Data and Selected Data - clears the sieve data in use and any selected screens and proppants. Use to "reset" your working file.

6 - Select Screen. Select which screens you want to plot with. You must select this for each screen you want to add. A list of available screens will be provided.

7 - Select Proppant. Select which proppants you want to plot with. You must select this for each proppant you want to add. A list of available proppant will be provided.

8 - Select Units. Select which unit the sand sand sieve data is imported with (micron, mm, inch, mesh, phi). This script will use microns internally and for display.

10 - Perform Calculations. Determines the cumulative weight percentages and other factors.

11 - Print SRT Data. Outputs in the terminal the data calculated for all samples.

12 - Plot Results. Plots a series of useful graphs for analyzying the sand samples, and plots screen and proppant sizes to help determine which is suitable. There is a wide range of plots that could be made, but these are the ones I find most useful.

<img width="1512" height="909" alt="Figure_1" src="https://github.com/user-attachments/assets/ceeccb28-e296-40d1-bd4e-d7189bbb30ba" />

Top row from left: 

a) Percent weight retained chart for all samples. Useful for identifying any bimodal samples, and gives some characterization of the sand coarseness.

b) Uniformity Coefficient vs Depth, with lines indicating highly uniform to highly non-uniform

c) Fines and pore throat size. This provides the average pore through vs depth of the formation, an estimate of the mobile fine size, the largest particle that will pass through the average pore size, and the smallest particle that will bridge on the average pore size. Ideally the mobile fine size will either be below the smallest size to bridge, or above the largest pass size, indicating a tendency of the particles to either bridge deep in the formation or produce through. Mobile fines that fall in between indicate a tendency to plug. The mobile fines coefficient can help define this as well, with values less than 5 and greater than 15 showing less impairment. This same graph can be extended to screeen aperture and proppant pore throats in a similar way to determine the effectiveness of SAS or gravel packs.

d) d10 and screen size. With the selected screens, evaluate how the d10 of the sands compare to the screen aperture, a common method of standalone screen selection. Depending on the non-uniformity, the d40 or d70 may be other good characterizations of the formation.

Bottom row from left:

e) Cumulative weight retained for all samples.

f) Uniformity Coefficent vs d50. Provides an overview of how clean the sand is in general. A large d50 with high uniformity is a much better sand (big and clean sand) to work with than one with small d50 and high non-uniformity (small and silty/shale)

g) D50 proppant / d50 sand. Provides the D50 of the proppant divided by the d50 of each sand sample. The three red lines represent common ranges for gravel packs (up to 6), low stress HRWP and frac packs (between 8 and 10), and high stress frac packs (up to 10)

h) Proppant D50 and 6xd50. Plots the selecte proppant D50 against the 6xd50 of the sands. This is a common method of proppant selection for a gravel pack. Some solutions call for 6.5 or 7, which can be adjusted easily in the code. 

20 - Save file. Saves all information, including calculations and selected screens and proppants, to a JSON file.

0 - Quit. Quits program.


Future improvements will include user-selectable D50/d50 ratios, addition of frac packs and injectors to calculations, autoselection of size characterization, adding screen and proppant to the fines passing/bridging chart, perforation EHD sizing, and chart for individual sand sieve analysis.
