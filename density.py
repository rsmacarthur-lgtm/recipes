# grams per US cup unless noted. Sources: King Arthur ingredient weight chart,
# USDA, and manufacturer figures. Robert's rules:
#   flour 120 g/cup (King Arthur) except ATK-family recipes, handled separately
#   kosher salt = Diamond Crystal (what he uses); plain/table/sea salt = table salt
CUP = {
 # flours & dry baking
 "all-purpose flour":120,"flour":120,"ap flour":120,"unbleached flour":120,"bread flour":120,
 "whole wheat flour":113,"whole-wheat flour":113,"cake flour":113,"rye flour":102,"semolina":167,
 "semolina flour":167,"almond flour":96,"cornmeal":138,"corn meal":138,"cornstarch":113,
 "oats":89,"rolled oats":89,"quick-cooking oats":89,"quick oats":89,"bran":58,
 "baking powder":192,"baking soda":220,"instant yeast":150,"active dry yeast":150,"yeast":150,
 "cream of tartar":144,"cocoa":84,"cocoa powder":84,"unsweetened cocoa":84,
 "breadcrumbs":108,"bread crumbs":108,"panko":50,
 # sugars & syrups
 "sugar":200,"granulated sugar":200,"white sugar":200,"caster sugar":200,"castor sugar":200,
 "brown sugar":213,"light brown sugar":213,"dark brown sugar":213,"packed brown sugar":213,
 "confectioners sugar":113,"powdered sugar":113,"icing sugar":113,
 "honey":340,"maple syrup":322,"molasses":337,"corn syrup":328,"malt syrup":336,
 # fats & dairy
 "butter":227,"unsalted butter":227,"salted butter":227,"melted butter":227,
 "shortening":205,"crisco":205,"lard":205,
 "olive oil":216,"extra-virgin olive oil":216,"extra virgin olive oil":216,"good olive oil":216,
 "vegetable oil":218,"canola oil":218,"oil":218,"sesame oil":218,"peanut oil":216,"sunflower oil":218,
 "milk":244,"whole milk":244,"buttermilk":242,"heavy cream":238,"cream":238,"half-and-half":242,
 "sour cream":230,"yogurt":245,"greek yogurt":245,"creme fraiche":230,"mayonnaise":220,
 "ricotta":246,"cottage cheese":226,"condensed milk":306,"evaporated milk":252,"coconut milk":240,
 # cheeses (grated/shredded)
 "grated parmesan":90,"parmesan":90,"parmigiano-reggiano":90,"grated parmigiano-reggiano":90,
 "pecorino":90,"grated pecorino":90,"shredded cheese":113,"grated cheese":113,"cheddar":113,
 "shredded cheddar":113,"mozzarella":113,"shredded mozzarella":113,"gruyere":113,"feta":150,
 # liquids
 "water":237,"stock":240,"chicken stock":240,"beef stock":240,"vegetable stock":240,
 "broth":240,"chicken broth":240,"beef broth":240,"vegetable broth":240,
 "wine":237,"white wine":237,"red wine":237,"dry white wine":237,"dry red wine":237,"marsala":237,
 "sake":237,"sherry":237,"vermouth":237,"beer":237,"rum":221,"bourbon":221,"brandy":221,
 "lemon juice":244,"lime juice":244,"orange juice":248,"juice":244,"vinegar":239,
 "white vinegar":239,"cider vinegar":239,"red wine vinegar":239,"balsamic vinegar":253,
 "rice vinegar":239,"white wine vinegar":239,"soy sauce":255,"fish sauce":255,
 "worcestershire":240,"tomato sauce":245,"tomato puree":250,"tomato paste":262,"ketchup":270,
 "salsa":260,"hot sauce":240,"tabasco":240,"dijon mustard":249,"mustard":249,"molasses":337,
 # nuts, seeds, chocolate, fruit
 "walnuts":117,"chopped walnuts":117,"pecans":109,"chopped pecans":109,"almonds":143,
 "sliced almonds":92,"slivered almonds":108,"peanuts":146,"pine nuts":135,"pistachios":123,
 "cashews":137,"macadamia nuts":134,"hazelnuts":135,
 "chocolate chips":170,"semisweet chocolate chips":170,"chopped chocolate":170,"chocolate":170,
 "raisins":145,"currants":145,"dried cranberries":120,"coconut":85,"shredded coconut":85,
 "sesame seeds":144,"poppy seeds":145,"flax seed":150,"sunflower seeds":140,"pumpkin seeds":129,
 # grains, pasta, legumes
 "rice":185,"white rice":185,"arborio rice":200,"carnaroli rice":200,"wild rice":160,
 "farro":200,"quinoa":170,"barley":200,"couscous":173,"lentils":192,"red lentils":192,
 "chickpeas":164,"black beans":172,"white beans":180,"cannellini beans":180,"kidney beans":177,
 # produce (chopped, packed as commonly measured)
 "chopped onion":160,"onion":160,"chopped yellow onion":160,"diced onion":160,
 "chopped celery":101,"celery":101,"chopped carrots":128,"carrots":128,"diced carrots":128,
 "chopped leeks":89,"leeks":89,"sliced leeks":89,"chopped shallots":160,"shallots":160,
 "corn":154,"frozen corn":154,"peas":145,"frozen peas":145,"mushrooms":70,"sliced mushrooms":70,
 "cherry tomatoes":149,"chopped tomatoes":180,"diced tomatoes":180,
 "spinach":30,"chopped spinach":180,"kale":67,"arugula":20,"lettuce":47,"cabbage":89,
 "olives":135,"chopped olives":135,"capers":142,"pickles":155,
 # herbs & spices (fresh chopped / ground) — per cup
 "chopped parsley":60,"parsley":60,"chopped fresh parsley":60,"chopped basil":24,"basil":24,
 "chopped cilantro":46,"cilantro":46,"chopped dill":45,"dill":45,"chopped mint":45,"mint":45,
 "chopped chives":48,"chives":48,"chopped rosemary":55,"rosemary":55,"chopped thyme":55,"thyme":55,
 "chopped sage":55,"sage":55,"chopped tarragon":55,"tarragon":55,"chopped oregano":55,"oregano":55,
}
# ground spices and a few others are better defined per teaspoon
TSP = {
 "table salt":6.0,"salt":6.0,"fine sea salt":6.0,"sea salt":5.5,"kosher salt":2.8,
 "morton kosher salt":4.8,"diamond crystal kosher salt":2.8,"flaky sea salt":2.5,
 "black pepper":2.3,"ground black pepper":2.3,"pepper":2.3,"white pepper":2.4,
 "ground cumin":2.1,"cumin":2.1,"ground coriander":1.8,"coriander":1.8,
 "paprika":2.3,"smoked paprika":2.3,"cayenne":1.8,"chili powder":2.6,"chile powder":2.6,
 "ground cinnamon":2.6,"cinnamon":2.6,"ground ginger":1.8,"ground nutmeg":2.2,"grated nutmeg":2.2,
 "nutmeg":2.2,"ground cloves":2.1,"cloves":2.1,"ground allspice":1.9,"allspice":1.9,
 "turmeric":3.0,"ground turmeric":3.0,"curry powder":2.0,"garlic powder":2.8,"onion powder":2.4,
 "dried oregano":1.0,"dried thyme":1.0,"dried basil":1.0,"dried sage":0.7,"dried rosemary":1.2,
 "red pepper flakes":1.8,"red-pepper flakes":1.8,"crushed red pepper":1.8,"fennel seeds":2.0,
 "vanilla extract":4.2,"almond extract":4.2,"extract":4.2,"lemon zest":2.0,"grated lemon zest":2.0,
 "orange zest":2.0,"lime zest":2.0,"zest":2.0,"minced garlic":2.8,"garlic":2.8,"grated ginger":2.0,
 "minced ginger":2.0,"ginger":2.0,"dry mustard":2.2,"mustard powder":2.2,"celery seed":2.0,
 "baking powder":4.0,"baking soda":4.6,"cornstarch":2.6,"instant yeast":3.1,"active dry yeast":3.1,
 "yeast":3.1,"cream of tartar":3.1,"sugar":4.2,
 
}

CUP.update({
 "vanilla":208,"margarine":227,"catsup":270,"ketchup":270,"horseradish":240,
 "prepared horseradish":240,"creme fraiche":230,"crème fraîche":230,"sour cream":230,
 "green onions":100,"sliced green onions":100,"scallions":100,"chopped onions":160,
 "chopped onion":160,"chopped carrot":128,"blue cheese":135,"crumbled blue cheese":135,
 "broccoli florets":91,"broccoli":91,"cauliflower":107,"zucchini":124,"squash":124,
 "potato starch":152,"corn starch":113,"miso":275,"golden syrup":340,"bananas":225,
 "mashed bananas":225,"mashed ripe bananas":225,"apples":109,"sliced apples":109,
 "blueberries":148,"strawberries":144,"raspberries":123,"cranberries":100,
 "pumpkin":245,"pumpkin puree":245,"applesauce":244,"peanut butter":258,"tahini":240,
 "grits":156,"polenta":157,"couscous":173,"orzo":200,"bulgur":140,"wheat berries":192,
 "chow mein noodles":45,"crackers":100,"graham cracker crumbs":100,"ritz crackers":100,
 "butterscotch chips":170,"white chocolate chips":170,"toffee bits":160,
 "marshmallows":50,"mini marshmallows":50,"jam":320,"jelly":320,"preserves":320,
 "cream cheese":232,"mascarpone":230,"swiss cheese":113,"monterey jack":113,"jack cheese":113,
 "provolone":113,"asiago":90,"romano":90,"blue cheese crumbles":135,
 "chicken":140,"cooked chicken":140,"diced chicken":140,"shredded chicken":140,
 "crabmeat":135,"shrimp":150,"bacon":115,"crumbled bacon":115,"ham":150,"diced ham":150,
})
TSP.update({
 "vanilla":4.2,"soda":4.6,"baking soda":4.6,"chilli powder":2.6,"marjoram":1.0,
 "saffron":0.7,"saffron threads":0.7,"espresso powder":2.0,"instant espresso":2.0,
 "coffee powder":2.0,"finely ground coffee":2.5,
 "fennel pollen":1.5,"celery salt":5.5,"old bay":2.4,"italian seasoning":1.0,
 "herbes de provence":1.0,"za'atar":2.0,"sumac":2.4,"cardamom":2.0,"ground cardamom":2.0,
 "star anise":2.0,"bay leaf":0.6,"poultry seasoning":1.5,"mustard seed":3.3,
 "sesame seeds":3.0,"poppy seeds":2.8,"cornmeal":2.9,"flour":2.5,"all-purpose flour":2.5,
 "sugar":4.2,"brown sugar":4.4,"confectioners sugar":2.4,"powdered sugar":2.4,"cocoa":1.8,
 
 
 
 
})

CUP.update({
 "blackberries":144,"sour cherries":154,"red grapes":151,"grapes":151,"prunes":174,
 "rhubarb":122,"summer fruit":150,"peaches":154,"sliced peaches":154,
 "half and half":242,"sharp cheese":113,"miracle whip":220,"mayonaise":220,
 "fontina":113,"grana padano":90,"gruyere cheese":113,
 "grated raw potatoes":150,"yukon gold potato":150,"potato":150,"potatoes":150,
 "apple cider":240,"cider":240,"prepared coffee":237,"strong coffee":237,"coffee":237,
 "cherry or grape tomatoes":149,"grape tomatoes":149,"halved cherry":149,
 "radish":116,"radishes":116,"preserved radish":150,"asparagus":134,
 "green peppers":149,"green pepper":149,"tomatillos":132,"green chiles":140,"chiles":140,
 "cucumber":133,"seedless cucumber":133,"fennel":87,"chopped fennel":87,"fennel fronds":20,
 "white onions":160,"sliced onions":160,"diced onions":160,"chopped yellow onions":160,
 "mung bean sprouts":104,"bean sprouts":104,"brussels sprouts":88,
 "cooked green beans":125,"green beans":125,
 "grand marnier":240,"framboise":240,"triple sec":240,"orange liqueur":240,"liqueur":240,
 "madeira":237,"vodka":221,"simple syrup":280,"karo syrup":328,
 "pecan halves":99,"walnut pieces":117,"nut meats":117,"nuts":130,"unsalted nuts":130,
 "chopped nuts":117,"blanched almond":143,"pepitas":129,"einkorn":190,
 "egg whites":243,"egg yolks":243,"egg white":243,"egg yolk":243,
 "bread":45,"bread cubes":45,"country bread":45,"white bread":45,"torn bread":45,
 "pasta":100,"small pasta":100,"tubetini":100,
 "pizza sauce":245,"pad thai sauce":240,"peanut sauce":240,"thai-style peanut sauce":240,
 "hoisin sauce":270,"hoisin":270,"sriracha":275,"sriracha chili sauce":275,
 "sesame paste":240,"chinese sesame paste":240,"tamarind concentrate":260,
 "harissa":256,"curry paste":256,"thai green curry paste":256,"lemongrass paste":256,
 "chipotle chiles in adobo":240,"sambal oelek":256,"picante sauce":250,"pace picante sauce":250,
 "bloody mary mix":240,"durkee sauce":240,"wickles relish":155,"relish":155,
 "lemon marmalade":320,"marmalade":320,"guacamole":230,"pectin":160,
 "french fried onions":40,"fried onions":40,"chex":30,"wheat chex":30,
 "olive slices":135,"ripe olive slices":135,"sun-dried tomatoes":110,
 "cooked turkey":140,"leftover cooked turkey":140,"evoo":216,
 "pickling spices":96,"dijon-style":249,"oj":248,"fresh oj":248,
})
TSP.update({
 "gravy master":4.9,"quick-cooking tapioca":3.0,"tapioca":3.0,"mace":1.7,
 "black peppercorns":2.9,"peppercorns":2.9,"crushed black peppercorns":2.9,
 "gelatin":3.2,"chipotle powder":2.3,"garam masala":2.0,"amchur":2.5,
 "cinnamin":2.6,"fennel seed":2.0,"vanilla-butternut flavor":4.2,
 "chili flakes":1.8,"parsely":1.25,
})

CUP.update({'creme fraiche': 230})
