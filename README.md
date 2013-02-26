================
HTMLDOM LIBRARY
================

HTMLDOM Library provides a simple interface for accessing and manipulating HTML documents.
You may find this library useful for building applications like screen-scraping. Typical 
usage often looks like this::
	#!/usr/bin/python
	from htmldom import htmldom	
	dom = htmldom.HtmlDom(url)
	dom.createDom()
	#Find all the links which contains the text specified in "contains()" function argument.
	#find() functions returns HtmlNodeList
	links = dom.find("a").contains(some_text)
	print(links.length())

The function names used in this library is similar to "jquery" and the library also supports CSS2 based selection.
The following section describes the functions available in this library.

HtmlDom Functions:
==================

1.find(selector): 
		  This function accepts a "css" selector and returns a HtmlNodeList object.

HtmlNodeList Functions:
=======================

1.children():
		This function returns a list of children(direct) nodes of the nodes present in the current set.
		The returned set is encapsulated into a HtmlNodeList object.
2.html():
		This function returns the html data associated with the nodes present in the current set.
		e.g.
		HTML Text:
			<div>Good <span>Morning</span> </div>
		then:
			html = dom.find("div").html()
			==> '<div>Good <span>Morning</span> </div>' #The enclosing "div" will be retained as it is.
3.text():
		This function returns the text data associated with the nodes present in the current set.
		e.g.
		HTML Text:
			<div>Good <span>Morning</span> </div>
		then:
			text = dom.find("div").text()
			==> 'Good Morning'
			
4.filter(selector):
		 	This function is used to reduce the current set to more specific set.
		 	This function accepts a css selector.
		 	Returns HtmlNodeList object.
		 	e.g.
		 	#Returns all the divs present in the page.
		 	divs = dom.find("div")
			#Filter only those divs which contains class ".one"
			divOne = divs.filter(".one")
5._not(selector):
			This function is the reverse of the filter function described above.
			This function accepts a css selector.
			Returns HtmlNodeList object.
			e.g.
			#Returns all the divs present in the page.
			divs = dom.find("div")
			#Returns only those which do not contain the class ".one"
			divNotOne = divs._not(".one")
6.eq(index):
			This function is used to index the nodes present in the current set.
			Returns HtmlNodeList object which encapsulates the indexed node object.
			e.g.
			#Returns the first "a" in the set.
			a = dom.find("a").eq(0)
7.first():
			This function returns the first node in the list.
			Returns HtmlNodeList object which encapsulates the indexed node object.
			e.g.
			#Returns the first "a" in the set.
			a = dom.find("a").first()
8.last():
			This function returns the last node in the list.
			Returns HtmlNodeList object which encapsulates the indexed node object.
			e.g.
			#Returns the last "a" in the set.
			a = dom.find("a").last()
9.has(selector):
			This function can be used to select only those nodes(from the current set) if they
			contain the nodes specified by the css selector.
			Returns HtmlNodeList object.
			e.g.
			#Select only those divs which contain "a" within them.
			divs = dom.find("div").has("a")
10._is(selector):
			This function can be used to check whether a particular node in present in the current set.
			returns True if the node is present specified by the css selector else false.
			e.g.
			var = dom.find("div").children()
			#If table is present in the current set
			if var._is("table"):
				print("table element is present")
			else:
				print("No table element is present")
11.next():
			This function returns the next siblings of the nodes present in the current set.
			Only immediate sibling is selected.
			Returns HtmlNodeList object.
			e.g.
			HTML Text:
				<p id='1'>One</p>
				<p id='2'>Two</p>
				<span id='3'>Three</span>
			then:
				sib = dom.find("p").next()
				==> [p#2,span#3]
11.nextAll():
			This function returns all the next siblings of the nodes present in the current set.
12.nextUntil(selector):
			This function similar to nextAll() but the returned set will not include those nodes which 
			comes after the node specified by the css selector and node itself.
			e.g.
			HTML Text:
				<p id='1'>One</p>
				<p id='2'>Two</p>
				<span id='3'>Three</span>
			then:
				sib = dom.find("p").nextUntil("span")
				==>[p#2]
				
13.prev(),14.preAll()
,15.prevUntil(selector):
			These functions are the counterparts of next(),nextAll() and nextUntil(selector)
			
16.siblings():
		        This function returns all the siblings of the node present in the current set.
		
17.parent():
			This function returns immediate parent of the all the nodes present in the current set.
		
18.parents():
			This function returns parent of all nodes and parent of their parent including the root node html.
		
19.parentsUntil(selector):
			This function is similar to parents() but the returned set will not include those 
			nodes which comes after the node specified by the css selector and node itself.
			
20.contains(regEx):
			This function returns only those nodes which contain the specified pattern inside them.
			e.g.
			HTML Text:
				   <a href="" id='1'>One</a>
				   <div>
				       <a href="" id='2'>Two</a>
				       <a href="" id='3'>Good Morning Two</a>
				   </div>
			then:
				a = dom.find("a").contains("Two")
				==>[a#2,a#3]
21.length():
			This function returns the number of nodes present in the current set.
22.write(filename):
			This function writes the html content of the nodes present in the set to the specified filename.
23.add(selector):
			This function adds new set of nodes to the current set.
			
24.find(selector):      
			This function gets the elements which are nested 
                        within the elements of the current set.
25.add(selector):
			This function adds a new set of elements to the current set.                  
