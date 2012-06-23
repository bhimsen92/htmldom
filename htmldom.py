"""
HTMLDOM Library provides a simple interface for accessing and manipulating HTML documents.
You may find this library useful for building applications like screen-scraping.
Inspired by Jquery Library.
"""
import re
import math
import traceback
import sys

elementName = r'<([\w_]+)'
restName = r'(?:\s+)?((?:[\w_:-]+\s*\=\s*[\'"](?:[^"]+)?[\'"]\s*;?)*)?\s*(?:/)?>'

#StartTag
startTag = re.compile(elementName + restName)

#endTag
endTag = re.compile(r'\s*</\s*([\w_]+)\s*>')


whiteSpace = re.compile(r'\s+')

#Used to spilt attributes into name/value pair i.e. ( class="one" ==> { 'class':'one' } )
attributeSplitter = re.compile(r'(?:([\w_:-]+)\s*\=\s*[\'"]([^"]+)[\'"]\s*)')

#These regex are used for class and id based selection.
"""
  i.e. given p.class#id
  @regVar:selector matches the "p" element and @regVar:left will contain ".class"
  and @regVar:right will hold the "#id" part.
"""
selector = re.compile(r'([\w_:-]+)?((?:[#.\[][%?&+\s\w_ /:.\d#(),;\]\'"=$^*-\\]+)*)?')

sep = r'(?:(?:[.#](?:[\w_:./-]+))'
leftSelector = r'|(?:\[\s*[\w_:-]+\s*(?:[$*^]?\s*\=\s*[\'"]\s*[^"\']+\s*[\'"])?\s*\]))?'
left = '('+sep + leftSelector+')'
right = r'((?:[%#.\[][^"]+)*)?'

newSelector = re.compile('(?:'+left + right+')?')

#This regex is used to detect [href*=someVal] | [href^=some_val] | [href$='someVal']
attributeSubStringSelector = re.compile(r'([*$^])\s*\=')

emptyElements = [ "br", "hr", "meta", "link", 
                  "base", "link", "img", "embed",
                  "param", "area", "col", "input",
                  "basefont", "frame", "isindex" ]
offset = 1 / 10000                  

class HtmlDomNode:
     def __init__( self, nodeName="text",nodeType=3):
          self.nodeName = nodeName
          self.nodeType = nodeType
          self.parentNode = None
          self.nextSiblingNode = None
          self.previousSiblingNode = None
          self.children = []
          self.attributes = {}
          self.ancestorList = []
          self.text = ""
          self.pos = -1
     def setParentNode( self, parentNode ):
          self.parentNode = parentNode
          return self
     def setSiblingNode( self, siblingNode ):
          self.nextSiblingNode = siblingNode
          return self
     def setPreviousSiblingNode( self, siblingNode ):
          self.previousSiblingNode = siblingNode
          return self
     def setChild( self, child ):
          self.children.append( child )
          return self
     def setAttributes( self, attributeDict ):
          self.attributes.update( attributeDict )
          return self
     def setAncestor( self, nodeList ):
          self.ancestorList = list(nodeList)
          return self
     def setText( self, text ):
          self.text = text
          return self
          
     def setAsFirstChild(self,node ):
          self.children.insert( 0, node )
          return self

     def setAncestorsForChildren( self, ancestor ):
          for childNode in self.children:
               if not childNode.ancestorList:
                    childNode.generateAncestorList()
               childNode.setAncestor( childNode.ancestorList + ancestor )
               childNode.setAncestorsForChildren( ancestor )
          return self
               
     def firstChild(self):
          return self.children[0]
     def lastChild(self):
          return self.children[-1]
          
     def getNextSiblingNode( self ):
        return self.nextSiblingNode
        
     def getPreviousSiblingNode(self):
          return self.previousSiblingNode
          
     def getAncestorList(self):
          return self.ancestorList
     def getName(self):
          return self.nodeName
     def html(self, spaces = 0 ):
          htmlStr = " " * spaces
          
          htmlStr += "<" + self.nodeName
          for attrName in self.attributes:
               htmlStr += " " + attrName +"="+'"'+" ".join(self.attributes[attrName]) + '"'
               
          htmlStr += '>'
          
          for node in self.children:
               if node.nodeType == 3:
                    htmlStr += "\n" + " " * ( spaces + 4 ) + node.text.strip()
               else:
                    htmlStr += "\n" + node.html( spaces + 4 )
                    
          htmlStr += "\n" + " " * spaces + '</'+self.nodeName +'>'
          return htmlStr

     def getText(self):
          textStr = ""
          for node in self.children:
               if node.nodeType == 3:
                    textStr += node.text
               else:
                    textStr += node.getText() + '\n'
          return textStr
     def getNextSiblings(self):
          siblingsSet = []
          node = self.nextSiblingNode
          while node:
               if node not in siblingsSet and node.nodeType != 3 :
                    siblingsSet.append(node)
               node = node.nextSiblingNode
          return siblingsSet
     def getPreviousSiblings(self):
          siblingsSet = []
          node = self.previousSiblingNode
          while node:
               if node not in siblingsSet and node.nodeType != 3:
                    siblingsSet.append(node)
               node = node.previousSiblingNode
          return siblingsSet
     def attr( self, attrName, val = False ):
          if val:
                self.attributes[ attrName ] = val.split()
               #return self.attributes.get( attrName, "Undefined Attribute" );
          else:
               return " ".join( self.attributes.get( attrName, ["Undefined","Attribute"] ) )
               
     def remove( self, node ):
         """
            This function must be called on parent node of the node.
            It removes the node from the parents child list and adjusts
            the sibling links.        
         """
         parent_node = self
         if parent_node:
            try:
                pos = parent_node.children.index( node )
                del parent_node.children[ pos ]
                if node.previousSiblingNode and node.nextSiblingNode:
                    node.previousSiblingNode.nextSiblingNode = node.nextSiblingNode
                    node.nextSiblingNode.previousSiblingNode = node.previousSiblingNode
            except ValueError:
                raise Exception( str( node ) + ": node is not a children of the parent node" )
                
         return node
         
     def append( self, node ):
        if isinstance( node, HtmlDomNode ):
            if len( self.children ) == 0:
                self.setChild( node )
            else:
                self.after( None, node )
            node.setParentNode( self )
            if not node.previousSiblingNode:
                node.pos = round( self.pos + ( offset / 10 ), 8 )
            else:
                node.pos = round( node.previousSiblingNode.pos + offset, 8 )
        else:
            raise Exception( "Invalid node object. object must be of type HtmlDomNode." )
     def prepend( self, node ):
        if isinstance( node, HtmlDomNode ):
            if len( self.children ) == 0:
                self.setAsFirstChild( node )
            else:
                self.before( None, node )
            node.setParentNode( self )
            if not node.previousSiblingNode:
                node.pos = round( self.pos + ( offset / 10 ), 8 )
            else:
                node.pos = round( node.previousSiblingNode.pos + offset, 8 )
        else:
            raise Exception( "Invalid node object. object must be of type Element." )
     def after( self, src, target ):
        """
            Function must be called on the parent node.
            This function sets target node after the src node.
            if src node is None then the target node will be set
            as the last child of the parent node.
        """
        flag = False
        currNextSiblingNode = None
        if src == None:
            src = self.lastChild()
            currNextSiblingNode = src.getNextSiblingNode()
            self.setChild( target )
            flag = True
        if isinstance( target, HtmlDomNode ) and isinstance( src, HtmlDomNode ):
            if not flag:
                currNextSiblingNode = src.getNextSiblingNode()
                index = self.children.index( src )
                self.children.insert( index + 1, target )
                target.setParentNode( self )
            
            src.setSiblingNode( target )
            target.setPreviousSiblingNode( src )
            target.setSiblingNode( currNextSiblingNode )
            if currNextSiblingNode:
                currNextSiblingNode.setPreviousSiblingNode( target )
            target.pos = round( src.pos + offset, 8 )
        else:
            raise Exception( "Invalid node object. object must be of type Element." )

     def before( self, src, target ):
        """
            Function must be called on the parent node.
            This function sets target node before the src node.
            if src node is None then the target node will be set 
            as the first child of the parent node.
        """
        flag = False
        currPrevSiblingNode = None
        if src == None:
            src = self.firstChild()
            currPrevSiblingNode = src.getPreviousSiblingNode()
            self.setAsFirstChild( target )
            flag = True
        if isinstance( target, HtmlDomNode ) and isinstance( src, HtmlDomNode ):
            if not flag:
                currPrevSiblingNode = src.getPreviousSiblingNode()
                try:
                    index = self.children.index( src )
                    self.children.insert( index, target )
                    target.setParentNode( self )
                    
                except ValueError:
                    raise Exception( "source node object must be children of the parent object" )
            src.setPreviousSiblingNode( target )
            target.setSiblingNode( src )
            target.setPreviousSiblingNode( currPrevSiblingNode )
            if currPrevSiblingNode :
                currPrevSiblingNode.setSiblingNode( target )
            target.pos = round( src.pos + offset, 8 )
        else:
            raise Exception( "Invalid node object. object must be of type HtmlDomNode." )
     
     def insertAfter( self, node ):
        """
            This Function is similar to after but here
            self is target node and "node" is the source node
        """     
        if isinstance( self, HtmlDomNode ) and isinstance( node, HtmlDomNode ):
            node.parentNode.after( node, self )
            
     def insertBefore( self, node ):
        """
            This Function is similar to before but here
            self is target node and node is the source node
        """
        if isinstance( self, HtmlDomNode ) and isinstance( node, HtmlDomNode ):
            node.parentNode.before( node, self )
     def copy( self ):
        """
            This function creats of the "self" node
        """
        n = None
        if self.nodeType == 1:
            n = HtmlDomNode( self.nodeName, self.nodeType )
            n.children = self.children
            n.attributes = self.attributes
        elif self.nodeType == 3:
            n = HtmlDomNode()
            n.text = self.text
        return n
        
     def generateAncestorList( self ):
        parent = self.parentNode
        while parent:
            self.ancestorList.append( parent )
            parent = parent.parentNode

class HtmlDom:
     def __init__( self, url="" ):
          self.baseURL = url

          #@var:domNodes is a dictionary which holds all the tags present in the page.
          # So that it will be very easy to look up the tags when queried.
          self.domNodes = {}
          self.domNodesList = []
          self.referenceToRootElement = None

     def createDom(self,htmlString=None):
          if htmlString:
               data = htmlString
               self.parseHTML( data )
               #self.domDictToList()               
          else:
               try:
                    try:
                         import urllib2
                    except ImportError:
                         #For python3
                         import urllib.request as urllib2
                    request = urllib2.Request(self.baseURL)
                    request.add_header('User-agent','Mozilla/9.876 (X11; U; Linux 2.2.12-20 i686, en; rv:2.0) Gecko/25250101 Netscape/5.432b1 (C-MindSpring)')
                    response = urllib2.urlopen(request)
                    data = response.read().decode( self.getEncoding( response ) )
                    self.parseHTML( data )
                    #self.domDictToList()
               except Exception as e:
                    print("Error while reading url: %s" % (self.baseURL))
                    #new_addition:@start
                    raise Exception
                    #new_addition:@end

          return self
     def parseHTML( self, data ):
          # pos is used in order to preserve their logical order of nodes in the document
          # because i am using dictionary datastructure to store the nodes so while retriving 
          # nodes their orders will be different. In order to avoid that i sort the set on 
          # "pos" variable[ sort_function:merge sort ]
          pos = 1
          index = 0
          #Node stack will hold the parent Nodes. The top most node will be the current parent.
          nodeStack = []
          while data:
              # to remove new lines.
               data = data.strip()
               #Doctype tag
               if data.find("<!DOCTYPE") == 0 or data.find("<!doctype") == 0:
                    #Just pass through the doctype tag.
                    index = data.find(">")
                    data = data[ index + 1:].strip()
                    continue
               #Comment Node
               if data.find("<!--") == 0:
                    #Just pass through the comment node.
                    index = data.find("-->")
                    data = data[index + len("-->"):].strip()
                    continue

               #index is just used for extracting texts withing the tags.
               #could change in future.
               index = data.find("<")

               # len(nodeStack) >= 1 means found text content between the end of a tag and the start of a new tag
               if len( nodeStack ) >= 1:
                    _index = -1
                    #if "script" element is on the top of the stack then entire content of it will be stored in a single text node
                    if nodeStack[-1].getName() == "script":
                         _index = data.find( "</script>" )
                         if _index != -1:
                              tmpData = data[ :_index ]
                    #if "style" element is on the top of the stack then entire content of it will be stored in a single text node
                    elif nodeStack[-1].getName() == "style":
                         _index = data.find("</style>")
                         if _index != -1:
                              tmpData = data[:_index]
                    else:
                         tmpData = data[:index]
                         
                    #tmpData should not be empty.
                    if tmpData:
                         textNode = HtmlDomNode("text")
                         textNode.setText(tmpData)
                         
                         textNode.pos = pos
                         pos += 1
                         
                         if len(nodeStack) > 0:
                              nodeStack[ -1 ].append( textNode )
                              textNode.setAncestor( nodeStack[::-1] )
                         if _index != -1:
                              data = data[_index:].strip()
                         else:
                              data = data[index:].strip()
                              
                    else:
                         data = data.strip()
               #end of a tag
               if data.find("</") == 0:
                    match = endTag.search( data )
                    data = data[len(match.group()):].strip()
                    try:
                         nodeStack.pop()
                         continue
                    except IndexError:
                         nodeStack = []

               #start of a tag.
               if data.find("<") == 0:
                    match = startTag.search( data )
                    if not match:
                         #Fail silently
                         continue
                         
                    #match.group(1) will contain the element name
                    elementName = match.group(1)
                    #new addition:  added lower function to the element name.
                    domNode = HtmlDomNode( elementName.lower(), 1 )
                    domNode.pos = pos
                    pos += 1
                    attr = match.group(2)
                    if attr:
                         #converting multispaces into single space.for easy handling of attributes
                         attr = whiteSpace.sub( ' ', attr.strip() )
                         attr = attributeSplitter.findall( attr )
                         attrDict = {}
                         for attrName,attrValues in attr:
                              attrDict[attrName] = attrValues.split()
                         domNode.setAttributes( attrDict )
                    if len(nodeStack) > 0:
                         # nodeStack[ -1 ] is a HtmlDomNode object
                         nodeStack[ -1 ].append( domNode )
                         #setting ancestor list
                         domNode.setAncestor( nodeStack[::-1] )
                         
                         #push the current node into the stack.so now domNode becomes the current parent node.
                         #if the current node is an empty element,do not push the element into the stack.
                         if elementName not in emptyElements:
                              nodeStack.append( domNode )
                    else:
                         domNode.setAncestor( nodeStack )
                         # nodeStack is a list
                         nodeStack.append( domNode )
                         self.referenceToRootElement = domNode

                    self.registerNode( domNode.nodeName, domNode )
                    data = data[len(match.group()):].strip()
               else:
                    if index == -1:
                        domNode = HtmlDomNode()
                        domNode.setText( data )
                        self.domNodesList.append( domNode )
                        data = data[ len( data ): ].strip()
                    else:
                        data = data[1:].strip()

     def registerNode( self, nodeName, domNode ):
          if self.domNodes.get(nodeName,None):
               #self.domNodes[nodeName].append( domNode )
               self.domNodes[ nodeName ] += self.getUniqueNodes( self.domNodes[ nodeName ], [ domNode ] )
          else:
               self.domNodes[ nodeName ] = [domNode]
               
     def updateDomNodes( self, newDomNodes ):
          for nodeName in newDomNodes:
               self.domNodes[nodeName] += newDomNodes[nodeName]
     def removeFromDomDict( self, node ):   
        if self.domNodes.get( node.nodeName, None ):
            try:
                pos = self.domNodes[ node.nodeName ].index( node )
                del self.domNodes[ node.nodeName ][ pos ]
            except ValueError:
                pass
        
     def getDomDict(self):
          return self.domNodes

     def domDictToList(self):
          for nodeName in self.domNodes:
               for selectedNode in self.domNodes[nodeName]:
                    #Converting the dictionary into a list of values.
                    self.domNodesList.append( selectedNode )
          self.domNodesList = list( set( self.domNodesList ) )
          sorted( self.domNodesList, key = lambda x: x.pos )
          return self.domNodesList
                    
     #new edition nList=[]
     #this addition is for find function for HtmlNodeList
     def find(self,selectors,nList=[]):
          classSelector = []
          idSelector = []
          attributeSelector = {}
          attributeSelectorFlags = {
                                     '$':False,'^':False,'*':False,'noVal':False
                                   }
          selectorMethod = {'+':False,'>':False}
          #new edition
          nodeList = nList
          
          # the following line is required for handling following kinds of inputs
          # "div+a" getConverted into "div + a". Now it is easy to split on spaces.
          selectors = re.sub(r'([+>])',r' \1 ',selectors)
          
          #normalizing the inputs.
          selectors = whiteSpace.sub( ' ', selectors )
          
          selectors = selectors.split()
          
          data = ""
          elemName = ""
          for value in selectors:
               if value == '+' or value == '>':
                    selectorMethod[value] = True
                    continue
               if value == '*':
                    return HtmlNodeList( self.domNodesList, self )
               
               match = selector.search( value )
               if match:
                    elemName = match.group(1)
                    data = match.group(2)
                    while data:
                         match = newSelector.search( data )
                         if match:
                              data = match.group(2)
                              #class selector
                              if match.group(1).find(".") == 0:
                                   index = match.group(1).find(".")
                                   classSelector.append( match.group(1)[index+1:] )
                              #id selector
                              elif match.group(1).find("#") == 0:
                                   index = match.group(1).find("#")
                                   idSelector.append( match.group(1)[index +1:] )
                              # attribute selector
                              elif match.group(1).find("[") == 0:
                                   index = match.group(1).find("]")
                                   attr = match.group(1)[1:][:-1]
                                   attrMatch = re.search( attributeSubStringSelector, attr )
                                   if attrMatch:
                                        attributeSelectorFlags[attrMatch.group(1)] = True
                                        _index = attr.find(attrMatch.group(1))
                                        attr = attr[:_index - len(attr)] + attr[_index + 1:]
                                        attr = attr.split("=")
                                   elif attr.find("=") == -1:
                                        #Only attribute name is given not the value.
                                        attributeSelectorFlags['noVal'] = True
                                        attr = attr.split()
                                        attr.append('')
                                   else:
                                        attr = attr.split("=")
                                   #new addition
                                   attr[1] = re.sub(r'[\'\"]?','',attr[1])
                                   #new addition
                                   attributeSelector[attr[0]] = attr[1]
                    if elemName:
                         nodes = self.domNodes.get( elemName, [] )
                    else:
                         if classSelector:
                              nodes = self.getNodesWithClassOrId(classSelector[-1],selectType='class')
                         elif idSelector:
                              nodes = self.getNodesWithClassOrId(idSelector[-1],selectType='id')
                         elif attributeSelector:
                              #new Addition:Mon 13 Feb
                              nodes = self.getNodesWithAttributes(attributeSelector,attributeSelectorFlags)
                    tmpList = []
                    for node in nodeList:
                         if selectorMethod['+']:
                              for selectedNode in nodes:
                                   if node.nextSiblingNode == selectedNode:
                                        tmpList +=self.getUniqueNodes(tmpList,[selectedNode])
                              selectorMethod['+'] = False
                         elif selectorMethod['>']:
                              for selectedNode in nodes:
                                   if selectedNode in node.children:
                                        tmpList +=self.getUniqueNodes(tmpList,[selectedNode])
                              selectorMethod['>'] = False
                         else:
                              for selectedNode in nodes:
                                   if not selectedNode.ancestorList:
                                        selectedNode.generateAncestorList()
                                   if node in selectedNode.ancestorList:
                                        tmpList +=self.getUniqueNodes(tmpList,[selectedNode])
                    if not nodeList:
                         tmpList = nodes
                    nodes = tmpList
                    nodeList = []
                    for node in nodes:
                         nodeAccepted = True
                         for value in classSelector:
                              if value not in node.attributes.get('class',[]):
                                   nodeAccepted = False
                                   break
                         if nodeAccepted:
                              for value in idSelector:
                                   if value not in node.attributes.get('id',[]):
                                        nodeAccepted = False
                                        break
                         if nodeAccepted:
                              if attributeSelector:
                                   nodeAccepted = self.getNodesWithAttributes(attributeSelector,attributeSelectorFlags,[node])
                         if nodeAccepted:
                              nodeList.append(node)
                    classSelector = []
                    idSelector = []
                    attributeSelector = {}
                    attributeSelectorFlags = {'$':False,'^':False,'*':False,'noVal':False}
               if not nodeList:
                    break
          
          sorted( nodeList, key = lambda x : x.pos )
          return HtmlNodeList( nodeList, self )
     def getNodesWithClassOrId( self,className="",nodeList = None,selectType=""):
          tmpList = []
          for nodeName in self.domNodes:
               [ tmpList.append( selectedNode ) for selectedNode in self.domNodes[nodeName] if className in selectedNode.attributes.get(selectType,['']) ]
          return tmpList
     def getNodesWithAttributes( self, attributeSelector,attributeSelectorFlags,nodeList = None):
          self.domDictToList()
          tmpList = self.domNodesList
          
          if nodeList:
               tmpList = nodeList
          key,attrValue = list(attributeSelector.items())[0]
          newList = []
          for node in tmpList:
               nodeAccepted = True
               if attributeSelectorFlags['$']:
                    if attributeSelector[key] not in node.attributes.get(key,[''])[-1][len(node.attributes.get(key,[''])[-1])::-1]:
                         nodeAccepted = False
               elif attributeSelectorFlags['^']:
                    if attributeSelector[key] not in node.attributes.get(key,[''])[0]:
                         nodeAccepted = False
               elif attributeSelectorFlags['*']:
                    if attributeSelector[key] not in " ".join(node.attributes.get(key,[])):
                         nodeAccepted = False
               elif attributeSelectorFlags['noVal']:
                    if key not in node.attributes:
                         nodeAccepted = False
               elif attributeSelector[key] != " ".join(node.attributes.get(key,[])):
                    nodeAccepted = False
               if nodeAccepted:
                    newList.append(node)
          return newList
     def getUniqueNodes(self,srcList, newList ):
          tmpList = []
          for selectedNode in newList:
               if selectedNode not in srcList:
                    tmpList.append( selectedNode  )
          return tmpList
     def getEncoding( self, response ):
          encoding = 'utf-8'
          for key,val in response.headers.items():
               if key == 'Content-Type':
                    encoding = val.split(";")
                    try:
                         encoding = encoding[1].split('=')[1].strip()
                    except IndexError:
                         encoding = 'utf-8'
                         break
                    break
          return encoding                    

class HtmlNodeList:
     def __init__( self, nodeList,dom,prevNodeList=[],prevObject = None):
          self.nodeList = nodeList
          self.htmlDom = dom
          # new addition
          self.len = len( self.nodeList )
          # used for iteration
          self.counter = 0
          
          self.previousNodeList = prevNodeList
          if not prevObject:
               self.referenceToPreviousNodeListObject = self
          else:
               self.referenceToPreviousNodeListObject = prevObject
               
     def __iter__( self ):
          self.counter = 0
          return self

     def __next__( self ):
          if self.counter >= self.len:
               raise StopIteration
          else:
               tmpObj = self.eq( self.counter )
               self.counter += 1
               return tmpObj
               
     def __getitem__( self, index ):
          if isinstance( index, int ):
              return self.eq( index )
          elif isinstance( index, slice ):
              return HtmlNodeList( self.nodeList[ index ], self.htmlDom, self.nodeList, self )
     
     def children(self, selector = None):
          childrenList = []
          for node in self.nodeList:
               [ childrenList.append(child) for child in node.children if child.nodeType == 1]
          #msort( childrenList, 0, len( childrenList ) - 1 )          
          if selector:
               return HtmlNodeList( childrenList, self.htmlDom, self.nodeList, self ).filter( selector )
          else:
               return HtmlNodeList( childrenList,self.htmlDom,self.nodeList,self)
          
     def html(self):
          htmlStr = ""
          for node in self.nodeList:
               htmlStr += node.html()
          return htmlStr
               
     def text(self):
          textStr = ""
          for node in self.nodeList:
               textStr += node.getText()
          return textStr
     
     def attr( self, attrName, val = False):
          if len( self.nodeList ) > 0 and not val:
               return self.nodeList[0].attr( attrName, val )
          elif val:
               for node in self.nodeList:
                    node.attr( attrName, val )
          else:
               raise IndexError

     def filter(self,selector):
          nList = self.htmlDom.find( selector )
          tmpList = []
          for node in self.nodeList:
               if node in nList.nodeList:
                    tmpList += self.getUniqueNodes( tmpList, [node] )
                    
          sorted( tmpList, key = lambda x : x.pos )

          return HtmlNodeList( tmpList,self.htmlDom, self.nodeList,self)
          
     def _not(self,selector ):
          nList = self.htmlDom.find( selector )
          tmpList = []
          for node in self.nodeList:
               if node not in nList.nodeList:
                    tmpList.append( node )
                    
          sorted( tmpList, key = lambda x : x.pos )
          return HtmlNodeList( tmpList,self.htmlDom, self.nodeList, self )
          
     def eq(self,index ):
          if index >= -len(self.nodeList) and index < len( self.nodeList ):
               return HtmlNodeList( [self.nodeList[index]], self.htmlDom, self.nodeList,self )
          else:
               return None
               
     def first( self ):
          return self.eq(0)
          
     def last( self ):
          return self.eq( len(self.nodeList ) - 1 )
          
     def has(self,selector ):
          nList = self.htmlDom.find( selector )
          tmpList = []
          for node in self.nodeList:
               for selectedNode in nList.nodeList:
                    if not selectedNode.ancestorList:
                        node.generateAncestorList()
                    if node in selectedNode.ancestorList:
                        tmpList += self.getUniqueNodes( tmpList, [ node ] )
          
          sorted( tmpList, key = lambda x: x.pos )
          return HtmlNodeList( tmpList,self.htmlDom, self.nodeList,self)
          
     def _is(self,selector):
          val = self.filter( selector )
          if val.nodeList:
               return True
          else:
               return False
               
     def next(self, selector = None):
          tmpList = []
          nextNode = None
          for node in self.nodeList:
               nextNode = node.nextSiblingNode
               while nextNode and nextNode.nodeType == 3:
                    nextNode = nextNode.nextSiblingNode
               if nextNode:
                    tmpList += self.getUniqueNodes( tmpList, [ nextNode ] )
          
          if selector:
               return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self ).filter( selector )
          else:
               sorted( tmpList, key = lambda x: x.pos )
               return HtmlNodeList( tmpList, self.htmlDom, self.nodeList,self)
     
     def nextAll(self, selector = None ):
          tmpList = []
          for node in self.nodeList:
               tmpList += self.getUniqueNodes( tmpList, node.getNextSiblings() )
               
          if selector:
               return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self ).filter( selector )
          else:
               sorted( tmpList, key = lambda x: x.pos )
               return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self)
     
     def nextUntil(self,selector):
          nList = self.htmlDom.find(selector)
          siblingsSet = []
          tmpList = []
          selectedNodeList = []
          for node in self.nodeList:
               #This function gets all the siblings.
               tmpList = node.getNextSiblings()
               for selectedNode in nList.nodeList:
                    try:
                         index = tmpList.index( selectedNode )
                         selectedNodeList = tmpList[:index]
                         siblingsSet += self.getUniqueNodes( siblingsSet, selectedNodeList )
                         break
                    except ValueError:
                         pass
               else:
                    siblingsSet += self.getUniqueNodes( siblingsSet, tmpList )
          sorted( siblingsSet, key = lambda x: x.pos )                    
          return HtmlNodeList( siblingsSet,self.htmlDom, self.nodeList, self)
     
     def prev(self, selector = None ):
          tmpList = []
          prNode = None
          for node in self.nodeList:
               prevNode = node.previousSiblingNode
               while prevNode and prevNode.nodeType == 3: # if its text node: loop
                    prevNode = prevNode.previousSiblingNode
               if prevNode:
                    tmpList += self.getUniqueNodes( tmpList, [ prevNode ] )
               
          if selector:
               return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self ).filter( selector )
          else:
               sorted( tmpList, key = lambda x: x.pos )            
               return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self)
     
     def prevAll( self, selector = None ):
          tmpList = []
          for node in self.nodeList:
               tmpList += self.getUniqueNodes( tmpList, node.getPreviousSiblings() )
          if selector:
               return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self ).filter( selector )
          else:
               sorted( tmpList, key = lambda x: x.pos )
               tmpList = tmpList[ :: -1 ]
               return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self)
     
     def prevUntil(self,selector):
          nList = self.htmlDom.find(selector)
          siblingsSet = []
          tmpList = []
          selectedNodeList = []
          for node in self.nodeList:
               #This function gets all the previous siblings.
               tmpList = node.getPreviousSiblings()
               for selectedNode in nList.nodeList:
                    try:
                         index = tmpList.index( selectedNode )
                         selectedNodeList = tmpList[:index]
                         siblingsSet += self.getUniqueNodes( siblingsSet, selectedNodeList )
                         break
                    except ValueError:
                         pass
               else:
                    siblingsSet += self.getUniqueNodes( siblingsSet, tmpList )
                    
          sorted( siblingsSet, key = lambda x: x.pos )
          return HtmlNodeList( siblingsSet,self.htmlDom, self.nodeList, self )
      
     def siblings(self,selector=None):
          """
             This function gets all the siblings of each node present in the current 
             HtmlNodeList object.( including previous and next siblings )
          """
          prevSiblingsSet = []
          nextSiblingsSet = []
          siblingsSet = []
          for node in self.nodeList:
               prevSiblingsSet = node.getPreviousSiblings()
               siblingsSet += self.getUniqueNodes( siblingsSet, prevSiblingsSet )
               nextSiblingsSet = node.getNextSiblings()
               siblingsSet += self.getUniqueNodes( siblingsSet, nextSiblingsSet )          
          if selector:
               return HtmlNodeList( siblingsSet, self.htmlDom, self.nodeList, self ).filter( selector )
          else:
               sorted( siblingsSet, key = lambda x: x.pos )
               return HtmlNodeList( siblingsSet, self.htmlDom, self.nodeList,self )
          
     def parent( self, selector = None ):
          """
               This function gets all the parents, not just immediate parent
               of each node present in the current HtmlNodeList object.
               selector: It is used to filter the parent list means to select only specific parents.
          """     
          tmpList = []
          for node in self.nodeList:
               if node.parentNode:
                    tmpList.append(node.parentNode)                    
          if selector:
               return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self ).filter( selector )
          else:
               sorted( tmpList, key = lambda x: x.pos )
               return HtmlNodeList( tmpList, self.htmlDom, self.nodeList,self)
               
     def parents( self, selector = None ):
          """
               This function gets all the parents, not just immediate parent but parent of parent and so on..
               of each node present in the current HtmlNodeList object.
               selector: It is used to filter the parent list means to select only specific parents.
          """     
          tmpList = []
          for node in self.nodeList:
               if not node.ancestorList:
                    node.generateAncestorList()
               tmpList += self.getUniqueNodes( tmpList, node.ancestorList )
          if selector:
               return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self ).filter( selector )
          else:
               sorted( tmpList, key = lambda x: x.pos ) 
               return HtmlNodeList( tmpList, self.htmlDom, self.nodeList, self)

     def parentsUntil(self,selector):
          """
               This function gets all the parents, not just immediate parent but parent of parent and so on..
               of each node present in the current HtmlNodeList object until the parent specified by the 
               selector is reached.
          """
          nList = self.htmlDom.find(selector)
          parentsList = []
          tmpList = []
          selectedNodesList = []
          for node in self.nodeList:
               if not node.ancestorList:
                    node.generateAncestorList()                
               tmpList = node.ancestorList
               for selectedNode in nList.nodeList:
                    try:
                         index = tmpList.index( selectedNode )
                         selectedNodeList = tmpList[:index]
                         parentsList += self.getUniqueNodes( parentsList, selectedNodeList )
                         break
                    except ValueError:
                         pass
               else:
                    parentsList += self.getUniqueNodes( parentsList, tmpList )
          sorted( parentsList, key = lambda x: x.pos )                    
          return HtmlNodeList( parentsList, self.htmlDom, self.nodeList, self )
          
     def add(self,selector):
          """
             This function adds new elements to the current list.
          """     
          nList = self.htmlDom.find( selector )
          newNodeList = self.nodeList + self.getUniqueNodes( self.nodeList, nList.nodeList )
          sorted( newNodeList, key = lambda x: x.pos )
          return HtmlNodeList( newNodeList, self.htmlDom, self.nodeList,self )
          
     def andSelf(self):
          newList = []
          newList += self.getUniqueNodes( newList, self.previousNodeList )
          newList += self.getUniqueNodes( newList, self.nodeList )
          
          sorted( newList, key = lambda x: x.pos )
          return HtmlNodeList( newList, self.htmlDom, self.nodeList,self )
     
     def end(self):
          return HtmlNodeList( self.previousNodeList, self.htmlDom, self.referenceToPreviousNodeListObject.referenceToPreviousNodeListObject.nodeList,self.referenceToPreviousNodeListObject.referenceToPreviousNodeListObject )

     def find(self,selector):
          nList = self.htmlDom.find( selector,self.nodeList )
          return HtmlNodeList( nList.nodeList, self.htmlDom, self.nodeList, self )

     def write( self,fileName ):
          import codecs
          fp = codecs.open( fileName, "w","utf-8")
          fp.write( self.html() )
          fp.close()
          return self
     def length(self):
          return len(self.nodeList)
     def contains( self, pattern ):
          pattern = re.compile( pattern )
          selectedNodeList = []
          for node in self.nodeList:
            text = node.getText()
            if pattern.search( text ):
              selectedNodeList += self.getUniqueNodes( selectedNodeList, [node] )
              
          sorted( seletedNodeList, key = lambda x: x.pos )
          return HtmlNodeList( selectedNodeList, self.htmlDom, self.nodeList, self )
          
     def toList(self):
         return self.nodeList
     
     def append( self, nodes,type_ = None ):
        flag = False
        if isinstance( nodes, HtmlNodeList ):
            nodes = nodes.toList()
        elif isinstance( nodes, list ):
            nodes = nodes
        elif isinstance( nodes, str ):# and not type_:
            h = HtmlDom().createDom( nodes )
            h.domDictToList()
            nodes = h.domNodesList
            tmpList = []
            other_nodes = []
            flag = True
            for node in nodes:
                if not node.parentNode:
                    tmpList.append( node )
                else:
                    self.htmlDom.registerNode( node.nodeName, node )
                    other_nodes.append( node )
            nodes = tmpList
            sorted( nodes, key = lambda x: x.pos )
        else:
            nodes = [ nodes ]
        if len( self.nodeList ) == 1:
            for node in nodes:
                self.htmlDom.removeFromDomDict( node )                    
                if node.parentNode:
                    node.parentNode.remove( node )      
                self.nodeList[ 0 ].append( node )
                self.htmlDom.registerNode( node.nodeName, node )
        else:
            removedAll = False
            for eachNode in self.nodeList:
                for node in nodes:            
                    if not removedAll and node.parentNode:
                        self.htmlDom.removeFromDomDict( node )
                        try:
                            if node.parentNode:
                                node.parentNode.remove( node )
                        except Exception:
                            removedAll = True
                    node_c = node.copy()
                    eachNode.append( node_c )
                    self.htmlDom.registerNode( node_c.nodeName, node_c )
        if flag:
            for node in other_nodes:
                if not node.previousSiblingNode:
                    node.pos = round( node.parentNode.pos + ( offset / 10 ), 12 )
                else:
                    node.pos = round( node.previousSiblingNode.pos + offset, 12 )
        return self
                
     def prepend( self, nodes, type_ = None ):
        flag = False
        if isinstance( nodes, HtmlNodeList ):
            nodes = nodes.toList()[::-1]
        elif isinstance( nodes, list ):
            nodes = nodes[ ::-1]
        elif isinstance( nodes, str ):# and not type_:
            h = HtmlDom().createDom( nodes )
            h.domDictToList()
            nodes = h.domNodesList
            tmpList = []
            other_nodes = []
            flag = True
            for node in nodes:
                if not node.parentNode:
                    tmpList.append( node )
                else:
                    self.htmlDom.registerNode( node.nodeName, node )
                    other_nodes.append( node )
            nodes = tmpList
            sorted( nodes, key = lambda x: x.pos )
            nodes = nodes[::-1]
        else:
            nodes = [ nodes ]
        if len( self.nodeList ) == 1:
            for node in nodes:
                self.htmlDom.removeFromDomDict( node )
                if node.parentNode:
                    node.parentNode.remove( node )
                self.nodeList[ 0 ].prepend( node )
                self.htmlDom.registerNode( node.nodeName, node )
        else:
            removedAll = False
            for eachNode in self.nodeList:
                for node in nodes:            
                    if not removedAll and node.parentNode:
                        self.htmlDom.removeFromDomDict( node )
                        try:
                            if node.parentNode:
                                node.parentNode.remove( node )
                        except Exception:
                            removedAll = True
                    node_c = node.copy()
                    eachNode.prepend( node_c )
                    self.htmlDom.registerNode( node_c.nodeName, node_c )
        if flag:
            for node in other_nodes:
                if not node.previousSiblingNode:
                    node.pos = round( node.parentNode.pos + ( offset / 10 ), 12 )
                else:
                    node.pos = round( node.previousSiblingNode.pos + offset, 12 )
        return self
     def after( self, nodes, type_ = None ):
        flag = False
        if isinstance( nodes, HtmlNodeList ):
            nodes = nodes.toList()[::-1]
        elif isinstance( nodes, list ):
            nodes = nodes[::-1]
        elif isinstance( nodes, str ):# and not type_:
            h = HtmlDom().createDom( nodes )
            h.domDictToList()
            nodes = h.domNodesList
            tmpList = []
            other_nodes = []
            flag = True
            for node in nodes:
                if not node.parentNode:
                    tmpList.append( node )
                else:
                    self.htmlDom.registerNode( node.nodeName, node )
                    other_nodes.append( node )
            nodes = tmpList
            sorted( nodes, key = lambda x: x.pos )
            nodes = nodes[ ::-1 ]
        else:
            nodes = [ nodes ]
        if len( self.nodeList ) == 1:
            parent = self.nodeList[ 0 ].parentNode
            for node in nodes:
                if node.parentNode:
                    node.parentNode.remove( node )
                self.htmlDom.removeFromDomDict( node )
                if parent:
                    parent.after( self.nodeList[ 0 ], node )
                else:
                    self.nodeList[ 0 ].after( None, node )
                self.htmlDom.registerNode( node.nodeName, node )
        else:
            removedAll = False
            for eachNode in self.nodeList:
                for node in nodes:            
                    if not removedAll and node.parentNode:
                        self.htmlDom.removeFromDomDict( node )
                        try:
                            if node.parentNode:
                                node.parentNode.remove( node )
                        except Exception:
                            removedAll = True
                    node_c = node.copy()
                    parent = eachNode.parentNode
                    if parent:
                        parent.after( eachNode, node_c )
                    else:
                        eachNode.after( None, node_c )
                    self.htmlDom.registerNode( node_c.nodeName, node_c )
        if flag:
            for node in other_nodes:
                if not node.previousSiblingNode:
                    node.pos = round( node.parentNode.pos + ( offset / 10 ), 12 )
                else:
                    node.pos = round( node.previousSiblingNode.pos + offset, 12 )
        return self
     def before( self, nodes, type_ = None ):
        flag = False
        if isinstance( nodes, HtmlNodeList ):
            nodes = nodes.toList()
        elif isinstance( nodes, list ):
            nodes = nodes
        elif isinstance( nodes, str ):#and not type_:
            h = HtmlDom().createDom( nodes )
            h.domDictToList()
            nodes = h.domNodesList
            tmpList = []
            other_nodes = []
            flag = True
            for node in nodes:
                if not node.parentNode:
                    tmpList.append( node )
                else:
                    self.htmlDom.registerNode( node.nodeName, node )
                    other_nodes.append( node )
            nodes = tmpList            
            sorted( nodes, key = lambda x: x.pos )
        else:
            nodes = [ nodes ]
        if len( self.nodeList ) == 1:
            parent = self.nodeList[ 0 ].parentNode        
            for node in nodes:
                if node.parentNode:
                    node.parentNode.remove( node )
                self.htmlDom.removeFromDomDict( node )
                if parent:
                    parent.before( self.nodeList[ 0 ], node )
                else:
                    self.nodeList[ 0 ].before( None, node )
                self.htmlDom.registerNode( node.nodeName, node )                    
        else:
            removedAll = False
            for eachNode in self.nodeList:
                for node in nodes:            
                    if not removedAll and node.parentNode:
                        self.htmlDom.removeFromDomDict( node )
                        try:
                            if node.parentNode:
                                node.parentNode.remove( node )
                        except Exception:
                            removedAll = True
                    node_c = node.copy()
                    parent = eachNode.parentNode
                    if parent:
                        parent.before( eachNode, node_c )
                    else:
                        eachNode.before( None, node_c )
                    self.htmlDom.registerNode( node_c.nodeName, node_c )
        if flag:
            for node in other_nodes:
                if not node.previousSiblingNode:
                    node.pos = round( node.parentNode.pos + ( offset / 10 ), 12 )
                else:
                    node.pos = round( node.previousSiblingNode.pos + offset, 12 )
        return self
        
     def getNode( self ):
        return self.nodeList[ 0 ]
     
     def getUniqueNodes(self,srcList, newList ):
          tmpList = []
          for selectedNode in newList:
               if selectedNode not in srcList:
                    tmpList.append( selectedNode  )
          return tmpList

def createElement( nodeName ):
    return HtmlDomNode( nodeName, 1 )
    
def createTextElement( nodeVal ):
    elem = HtmlDomNode( "text", 3 )
    elem.setText( nodeVal )
    return elem


def msort( nList, low, high ):
    if low < high:
        mid = math.floor( ( low + high ) / 2 )
        msort( nList, low, mid )
        msort( nList, mid + 1, high )
        merge( nList, low, mid, high )

