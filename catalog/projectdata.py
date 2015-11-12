from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CategoryItem

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

category1 = Category(name='Movies', image='http://sdasia.co/wp-content/uploads/2015/08/Movie-Releases.jpg')

session.add(category1)
session.commit()

catItem1 = CategoryItem(name='Avengers: Age of Ultron', description='Robot Bent on Human Destruction', 
	                    price='$14.99', image='http://cdn.playbuzz.com/cdn/ec97966e-6d93-4cb2-85f9-8b7500b2814c/f94be820-3473-4abf-84b9-b3751b7afc5b.jpg', category=category1)

session.add(catItem1)
session.commit()

catItem2 = CategoryItem(name='Mad Max: Fury Road',
						description='The Future Belongs to the Mad', price='$14.99',
						image='http://ecx.images-amazon.com/images/I/91xy4RlK98L._SL1425_.jpg',
	                    category=category1)

session.add(catItem2)
session.commit()

catItem3 = CategoryItem(name='Mission Impossible: Rogue Nation',
						description='Ethan and team take on their most impossible mission yet', price='$14.99',
						image='http://i1.mirror.co.uk/incoming/article5818007.ece/ALTERNATES/s1227b/MIRogueNationMain.jpg',
	                    category=category1)

session.add(catItem3)
session.commit()

category2 = Category(name='Sporting Goods', image='http://www.lf.k12.de.us/wp-content/uploads/2015/03/Sports.png')

session.add(category2)
session.commit()

catItem1 = CategoryItem(name='Basketballs',
						description='Spalding NBA Official Game Basketball', price='$139.99',
						image='http://www.dickssportinggoods.com/graphics/product_images/pDSP1-20875273v750.jpg',
	                    category=category2)

session.add(catItem1)
session.commit()

catItem2 = CategoryItem(name = 'Baseball Bats',
						description = 'Louisville Slugger 180 Series Ash Bat',
						image = 'http://www.dickssportinggoods.com/graphics/product_images/pDSP1-18110261v750.jpg',
	                    price='$24.99', category=category2)

session.add(catItem2)
session.commit()

catItem3 = CategoryItem(name = 'Footballs',
						description = 'Nike Youth Spiral-Tech 3.0 Football',
						image = 'http://www.dickssportinggoods.com/graphics/product_images/pDSP1-21696322v750.jpg',
	                    price='$24.99', category=category2)

session.add(catItem3)
session.commit()

category3 = Category(name='Video Games', image='http://webclass.wths.net/student23/html%202/images/Videogames.jpg')

session.add(category3)
session.commit()

catItem1 = CategoryItem(name='Mass Effect', description='Save Humanity', 
	                    price='$59.99',
	                    image='http://cdn.akamai.steamstatic.com/steam/apps/17460/header.jpg?t=1414522510',
	                    category=category3)

session.add(catItem1)
session.commit()

catItem2 = CategoryItem(name='Fallout 4', 
						description='Fallout 4 is an upcoming open world action role-playing video game developed by Bethesda Game Studios and published by Bethesda Softworks.', 
	                    price='$59.99',
	                    image='http://static1.gamespot.com/uploads/screen_medium/1365/13658182/2877208-fallout4_upt2015_20150603_v2.jpg',
	                    category=category3)

session.add(catItem2)
session.commit()

catItem3 = CategoryItem(name='World of Warcraft', 
						description='You are not prepared',
						price='$59.99',
	                    image='http://us.blizzard.com/static/_images/games/burningcrusade/wallpapers/wall1/wall1-1600x1200.jpg',
	                    category=category3)

session.add(catItem3)
session.commit()
