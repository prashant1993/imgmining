# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 11:57:10 2015

@author: Prashant
"""

from numpy import *
from itertools import combinations
from time import strftime
from operator import itemgetter

def datetime_today():
    return strftime("_%a_%d_%b_%Y_%Hh_%Mmin_%Ss")
    #return '_'+str(datetime.today().hour)+'_'+str(datetime.today().minute)+'_'+str(datetime.today().microsecond)+'_'+str(datetime.today().day)+'_'+str(datetime.today().month)+'_'+str(datetime.today().year)

count = 0
class ClusterNode(object):
    def __init__(self,vec,left,right,distance=0.0,count=1):
        self.left = left
        self.right = right
        self.vec = vec
        self.distance = distance
        self.count = count # only used for weighted average

    def extract_clusters(self,dist):
        """ Extract list of sub-tree clusters from 
            hcluster tree with distance<dist. """
        if self.distance < dist:
            return [self]
        return self.left.extract_clusters(dist) + self.right.extract_clusters(dist)

    def get_cluster_elements(self):
        """    Return ids for elements in a cluster sub-tree. """
        return self.left.get_cluster_elements() + self.right.get_cluster_elements()

    def get_height(self):
        """    Return the height of a node, 
            height is sum of each branch. """
        return self.left.get_height() + self.right.get_height()

    def get_depth(self):
        """    Return the depth of a node, depth is 
            max of each child plus own distance. """
        return max(self.left.get_depth(), self.right.get_depth()) + self.distance

    def draw(self,draw,x,y,s,imlist,im):
        """    Draw nodes recursively with image 
            thumbnails for leaf nodes. """
    
        h1 = int(self.left.get_height()*175 / 2)
        h2 = int(self.right.get_height()*175 /2)
        top = y-(h1+h2)
        bottom = y+(h1+h2)
        
        # vertical line to children
        draw.line((x,top+h1,x,bottom-h2),fill=(0,0,0))    
        #print "draw vertical "                
        # horizontal lines 
        ll = self.distance*s
        draw.line((x,top+h1,x+ll,top+h1),fill=(0,0,0))    
        #print "draw horizontal~1 "
        draw.line((x,bottom-h2,x+ll,bottom-h2),fill=(0,0,0))        
        #print "draw horizontal~2 "
        
        # draw left and right child nodes recursively    
        self.left.draw(draw,x+ll,top+h1,s,imlist,im)
        #print "draw left"
        self.right.draw(draw,x+ll,bottom-h2,s,imlist,im)
        #print "draw right"

class ClusterLeafNode(object):
    def __init__(self,vec,id):
        self.vec = vec
        self.id = id

    def extract_clusters(self,dist):
        return [self] 

    def get_cluster_elements(self):
        return [self.id]

    def get_height(self):
        return 1

    def get_depth(self):
        return 0
       
    def draw(self,draw,x,y,s,imlist,im):
        global count
        nodeim = Image.open(imlist[self.id])
        #print "count : "+ str(count) + " " + str( imlist[self.id])
        nodeim.thumbnail([150,150])
        ns = nodeim.size
        im.paste(nodeim,[int(x),int(y-ns[1]//2),int(x+ns[0]),int(y+ns[1]-ns[1]//2)])
        count = count + 1


def L2dist(v1,v2):
    return sqrt(sum((v1-v2)**2))

    
def L1dist(v1,v2):
    return sum(abs(v1-v2))

def awesome_hcluster(features,imlist,distfcn=L2dist):
    """ Cluster the rows of features using 
        hierarchical clustering. """
    
    # cache of distance calculations
    distances = {}
    chk_dist = {}
    
    # initialize with each row as a cluster 
    node = [ClusterLeafNode(array(f),id=i) for i,f in enumerate(features)]
    cnt = 0
    loop_num = 0
    while len(node)>1:
        
        closest = float('Inf')
        
        # loop through every pair looking for the smallest distance
        
        for ni,nj in combinations(node,2):
            im1 = imlist[node.index(ni)]
            im2 = imlist[node.index(nj)]
            if (ni,nj) not in distances:
                cnt = cnt + 1
                distances[ni,nj] = distfcn(ni.vec,nj.vec)
                if (im1,im2) not in chk_dist:
                    chk_dist[im1,im2] = [distances[ni,nj]]
                elif (im1,im2) in chk_dist:
                    chk_dist[im1,im2].append(distances[ni,nj])
                #print cnt
            #else:
                
            d = distances[ni,nj]
            if d<closest:
                closest = d
                lowestpair = (ni,nj)

        ni,nj = lowestpair
        
        # average the two clusters
        new_vec = (ni.vec + nj.vec) / 2.0
        
        # create new node
        new_node = ClusterNode(new_vec,left=ni,right=nj,distance=closest)
        node.remove(ni)
        node.remove(nj)
        node.append(new_node)
        loop_num = loop_num + 1
        
    with open("datalogs//datalog"+datetime_today()+'.txt','wb') as doc:
        dict_keys = chk_dist.keys()
        dict_chk = {}
        for i in sorted(dict_keys, key= lambda dictKey: dictKey[0]):
            
            if(i[0] in dict_chk):
                dict_chk[i[0]].append([i[1],min(chk_dist[i])])
            else:
                dict_chk[i[0]] = [[i[1],min(chk_dist[i])]]
            
            if(i[1] in dict_chk):
                dict_chk[i[1]].append([i[0],min(chk_dist[i])])                
            else:                
                dict_chk[i[1]] = [[i[0],min(chk_dist[i])]]
        
        for j in sorted(dict_chk.keys()):
            doc.write(str(j) +' --> \n')
            #print dict_chk[j]
            for k in sorted(dict_chk[j],key = lambda chkKey: chkKey[1]):
                doc.write("  "+str(k[0]) + " : " + str(k[1]) + ' \n')
            
    #for chk in sorted(dict_keys, key= lambda dictKey: dictKey[0]):
    #    doc.write(str(chk) + " : " + str(min(chk_dist[chk])) + ' \n')
        
#    doc.close()

    return node[0]

from PIL import Image,ImageDraw
 
def draw_dendrogram(node,imlist,filename='clusters.jpg'):
    """    Draw a cluster dendrogram and save to a file. """
    
    # height and width
    rows = node.get_height()*200 #node.get_height()*20
    cols = 3000
    
    # scale factor for distances to fit image width
    s = float(cols-150)/node.get_depth()
    
    # create image and draw object
    im = Image.new('RGB',(cols,rows),(255,255,255))
    draw = ImageDraw.Draw(im)
    
    # initial line for start of tree
    draw.line((0,rows/2,20,rows/2),fill=(0,0,0))    
    
    # draw the nodes recursively
    node.draw(draw,20,(rows/2),s,imlist,im)
    im.save(filename)
    #im.show()

def req_hcluster_one_image(features,imlist,new_f,new_im,distfcn=L2dist):
    """ Cluster the rows of features using 
        hierarchical clustering. """
    
    # cache of distance calculations
    distances = {}
    chk_dist = {}
    
    # initialize with each row as a cluster 
    node = [ClusterLeafNode(array(f),id=i) for i,f in enumerate(features)]
    lnode = len(node)
    cnt = 0
    #loop_num = 0
    ni = ClusterLeafNode(array(new_f),id=lnode)
    im1 = new_im
    while cnt<lnode:
        nj = node[cnt]
        im2 = imlist[cnt]
        
        distances[ni,nj] = distfcn(ni.vec,nj.vec)
        if (im1,im2) not in chk_dist:
            chk_dist[im1,im2] = [distances[ni,nj]]
        elif (im1,im2) in chk_dist:
            chk_dist[im1,im2].append(distances[ni,nj])
        
        cnt = cnt + 1

    doc = open("datalogs//datalog"+datetime_today()+'.txt','wb')
    dict_keys = chk_dist.keys()
    dict_chk = {}
    
    for i in sorted(dict_keys, key= lambda dictKey: dictKey[0]):
        if(i[0] in dict_chk):
            dict_chk[i[0]].append([i[1],chk_dist[i]])#min(chk_dist[i])])
        else:
            dict_chk[i[0]] = [[i[1],chk_dist[i]]] #[[i[1],min(chk_dist[i])]]

    dchk_k = sorted(dict_chk.keys())
    srted_list = sorted(dict_chk[dchk_k[0]],key = lambda chkKey: chkKey[1])
    doc.write(str(dchk_k[0]) + ' --> ')    
    for k in srted_list:
            doc.write("  "+str(k[0]) + " : " + str(k[1]) + ' \n')                
    doc.close()
    return srted_list