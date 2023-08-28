
'background',  # [0, 0, 0]

'Banana skin', # [255, 255, 0]
 - 36% of banana weight is peel [https://cooking.stackexchange.com/questions/55353/which-average-weight-of-the-banana-is-edible-i-e-which-of-the-banana-is-no]
 - 183g banana weight unpeeled [https://cooking.stackexchange.com/questions/55353/which-average-weight-of-the-banana-is-edible-i-e-which-of-the-banana-is-no]
 - 15 cc is average volume of banana peel [from chatGPT lmao]
 - 3.3 mm is average banana peel thickness [https://www.sciencedirect.com/science/article/abs/pii/026087749400054D]

 - Density: 4.392 g/cc
 - Image Thickness: 5mm (a bit more than 3.3mm to account for stacking)

'Egg shell',   # [255, 255, 255]
 - egg shell thickness: 0.3mm [https://www.cobb-vantress.com/assets/457568dbce/Mert-Yalcinalp-Shell-Quality.pdf]

 - Density: 2.386 g/cc [https://www.tandfonline.com/doi/abs/10.1080/00071666808415718?journalCode=cbps20]
 - Image Thickness: 1.5mm (bc shells can be standing up)

'Lettuce leaf',# [146, 208, 80]

 - Density: 0.24 g/cc [https://www.aqua-calc.com/page/density-table/substance/green-blank-leaf-blank-lettuce-coma-and-blank-upc-column--blank-000651041025]
 - Image Thickness: 1cm (bc may be individual leaves, stacked leaves, or whole lettuce)

'Hard bread',  # [131, 60, 12]
 - Density: 0.25 g/cc [https://modernistcuisine.com/mc/bread-is-lighter-than-whipped-cream/]
 - Image Thickness: 1.25cm (about thickness of a slice)

'Cooked meat', # [160, 121, 191]
 - Density: 1.033 g/cc [https://www.sciencedirect.com/science/article/abs/pii/S0023643801907625]
 - Image Thickness: 2cm (about 1 patty thick)

'Onion skin',  # [183, 123, 104]

 - If Onion radius is 3.5cm, Onion skin thickness is 1.5mm, ratio of onion skin volume to unpeeled onion volume is: 0.001285
 - Unpeeled onion density: 1526.825 kg/m^3 -> 1.527 g/cc [https://www.agriculturejournal.org/volume8number3/engineering-properties-of-peeled-and-unpeeled-multiplier-onion/]
 - Peeled onion density: 1108.74 kg/m^3 -> 1.109 g/cc 

 > but this gives me density of 325.29 g/cc, which is def wrong

 - Density: 0.5 g/cc (pretending its wax paper) [https://www.paperonweb.com/density.htm]
 - Image Thickness: 0.8mm

'Potato skin', # [153, 76, 0]
 - Density: 0.47 g/cc [https://www.aqua-calc.com/page/density-table/substance/white-blank-potato-blank-skins-coma-and-blank-with-blank-adhering-blank-flesh-coma-and-blank-fried]
 - Image Thickness: 1.2mm

'apple core',  # [255, 0, 0]
 - Density: 0.53 g/cc [https://www.aqua-calc.com/page/density-table/substance/apples-coma-and-blank-raw-coma-and-blank-with-blank-skin-blank--op-includes-blank-foods-blank-for-blank-usda-quote-s-blank-food-blank-distribution-blank-program-cp--blank--op-quartered-blank-or-blank-chopped-cp-]
 - Image Thickness: 3.5cm

'Orange',      # [237, 125, 49]
 - Density: 1.3 g/cc [https://www.researchgate.net/publication/26552176_Some_physical_properties_of_orange_var_Tompson#:~:text=Volume%20and%20mass%20of%20the,and%201.03%20g%20cm%2D3.]
 - Image Thickness: 6cm

'Waffle',      # [255, 192, 0]
 - Density: 0.9 g/cc [https://en.wikipedia.org/wiki/Waffle#:~:text=The%20recommended%20density%20of%20a,plate%20of%20the%20waffle%20iron.]
 - Image Thickness: 1.2cm

'Apple peel',  # [192, 0, 0]
 - Density: 0.4 g/cc (bit less than apple core)
 - Image Thickness: 1.5mm

'Corn leaves', # [153, 153, 0]
 - Density: 0.08161 g/cc [https://thescipub.com/pdf/ajbbsp.2012.44.53.pdf]
 - Image Thickness: 0.7cm (bc we're using bulk density)

'cucumber',    # [68, 84, 106]
 - Density: 1 g/cc [https://jssae.journals.ekb.eg/article_55669.html]
 - Image Thickness: 2cm

'grape',       # [153, 0, 153]
 - Density: 0.64 g/cc [https://www.aqua-calc.com/page/density-table/substance/grapes-coma-and-blank-red-blank-or-blank-green-blank--op-european-blank-type-coma-and-blank-such-blank-as-blank-thompson-blank-seedless-cp--coma-and-blank-raw]
 - Image Thickness: 1.5cm

'Orange skin', # [255, 178, 102]
 - Density: 0.41 g/cc [https://www.aqua-calc.com/page/density-table/substance/orange-blank-peel-coma-and-blank-raw]
 - Image Thickness: 0.8cm

'Tea bag',     # [102, 51, 0]
 - Density: 0.41 g/cc [https://www.aqua-calc.com/page/density-table/substance/black-blank-loose-blank-leaf-blank-tea-coma-and-blank-upc-column--blank-011110884381]
 - Image Thickness: 0.6cm

'Avocado skin',# [102, 255, 178]
 - Density: 1.035 g/cc [https://www.researchgate.net/figure/Relationship-at-harvest-between-flesh-density-and-flesh-DM-of-Hass-avocado-n-525_fig1_223731970]
 - Image Thickness: 2mm

'Chicken bone',# [102, 102, 0]
 - Density: 1.85 g/cc [from chatGPT lmao]
 - Image Thickness: 0.6mm

'Cooked fish', # [91, 155, 213]
 - Density: 0.57 g/cc [https://www.aqua-calc.com/page/density-table/substance/fish-coma-and-blank-salmon-coma-and-blank-chinook-coma-and-blank-smoked-blank--op-cooked-cp-]
 - Image Thickness: 2cm