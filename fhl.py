# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 11:55:11 2015

@author: Prashant
"""

import os
import fhcluster
import numpy as np
import sys
from PIL import Image
import pylab
from time import strftime
from pymongo import MongoClient
import base64
import datetime

conndb = MongoClient("localhost",27017)
features_db = conndb['n_f_DB']
f_collection = features_db['features_arrays']

def imlist(path):
    imlist = [os.path.join(path,f) for f in os.listdir(path) if f.endswith('.jpg') or f.endswith('.JPG')]
    return imlist

def datetime_today():
    return strftime("_%a_%d_%b_%Y_%Hh_%Mmin_%Ss")

def create_features(path):
    ims = imlist(path)
    features = np.zeros([len(ims),512])
    
    for i,f in enumerate(ims):
        #print ' Image : '+str(f)+' to be added..'
        #img_str = ''
        #with open(f,'rb') as rimg:
        #    img_str = base64.b64encode(rimg.read())
        opimg = Image.open(f)
        im = np.array(opimg)
        h,edges = np.histogramdd(im.reshape(-1,3),8,normed=True,range=[(0,255),(0,255),(0,255)])
        features[i] = h.flatten()
        ##serialize to 1D
        ##record['feature1'] = features[i].tolist()
        #f_collection.insert({'im_loc':f,
        #                    'f_array':features[i].tolist(),
        #                    'date_added': datetime.datetime.today()
        #                    })
                            #'img_base64':img_str
                            
        
    #print 'Images in Path: ' + str(path) + ' have been added in the database'                         
    #print features,ims
    return features, ims 

def add_image(fea,pathnew_im,ims_b4):
    ims = imlist(pathnew_im)
    features = np.zeros([len(ims)+len(fea),512])
    
    for j in range(len(fea)):
        features[j] = fea[j]
    
    for i,f in enumerate(ims):
        ims_b4.append(f)
        #img_str = ''
        #with open(f,'rb') as rimg:
        #    img_str = base64.b64encode(rimg.read())
        im = np.array(Image.open(f))
        h,edges = np.histogramdd(im.reshape(-1,3),8,normed=True,range=[(0,255),(0,255),(0,255)])
        features[i+len(fea)] = h.flatten()
        #f_collection.insert({'im_loc':f,
        #                    'f_array':features[i].tolist(),
        #                    'date_added': datetime.datetime.today(),
        #                    'img_base64':img_str
        #                    })
                                
    return features,ims_b4

def result(features,ims):
    tree = fhcluster.awesome_hcluster(features,ims)
    img_name = 'Cluster_Images//NewClustersResults'+datetime_today()+'.jpg'    
    fhcluster.draw_dendrogram(tree,ims,img_name)
    b_val = ''    
    with open(img_name,'rb') as imgfile:
        b_val = base64.b64encode(imgfile.read())        
    return b_val

def req_result(features,ims,new_im):
    #new image
    f = np.zeros(512)
    im = np.array(Image.open(new_im))
    h,edges = np.histogramdd(im.reshape(-1,3),8,normed=True,range=[(0,255),(0,255),(0,255)])
    f = h.flatten()
    
    #search for best image
    srted = fhcluster.req_hcluster_one_image(features,ims,f,new_im)
    #b_val = ''    
    #with open(name,'rb') as imgfile:
    #    b_val = base64.b64encode(imgfile.read())        
    #return b_val,value
    return srted
    """
    obtained_list = fhcluster.req_hcluster_one_image(features,ims,f,new_im)
    req_list = []
    condition = True
    count = 0
    while(condition):
        if(obtained_list[count][0]<4.7e-06):
            req_list.append()
        count = count + 1
    """

def query_image(new_im):  
    a = f_collection.find({}, {"im_loc":1,"f_array":1})
    features = []
    ims = []
    for i in a:
        features.append(i['f_array'])
        ims.append(i['im_loc'])
    
    f = np.zeros(512)
    im = np.array(Image.open(new_im))
    h,edges = np.histogramdd(im.reshape(-1,3),8,normed=True,range=[(0,255),(0,255),(0,255)])
    f = h.flatten()
    
    obtained_list = fhcluster.req_hcluster_one_image(features,ims,f,new_im)
    req_list = []
    condition = True
    count = 0
    while(condition):
        if(obtained_list[count][1][0]<4e-06):
            name = obtained_list[count][0]
            b_val = ''
            with open(name,'rb') as imgfile:
                b_val = base64.b64encode(imgfile.read())        
            req_list.append([b_val,format(obtained_list[count][1][0]/4e-06, '.2f')])
            count = count + 1
        else:
            condition = False
    
    return req_list

def find_clusters(tree,cluster):
    # visualize clusters with some (arbitrary) threshold
    clusters = tree.extract_clusters(0.23*tree.distance)
    # plot images for clusters with more than 3 elements
    count = 0
    for c in clusters:
        elements = c.get_cluster_elements()
        nbr_elements = len(elements)
        if nbr_elements>3:
            directory = str('\\Cluster\\') #sys.argv[2][:-4]+'\\Cluster\\')
            if not os.path.exists(directory):
                os.makedirs(directory)
            pylab.figure()
            for p in range(min(nbr_elements,20)):
                pylab.subplot(4,5,p+1)
                im = np.array(Image.open(imlist[elements[p]]))
                im.save(str(sys.argv[2]+str(p)))
                print 'Image Clusters : Image File ' +str(sys.argv[2]+str(p)) + '.jpg' + ' Saved'
                pylab.imshow(im)
                pylab.axis('off')
    
            pylab.savefig(str(directory+str(count)+'.jpg'))
            count = count+1

#initial_path = 'H:\\ProjectImageMining\\Images'

#dirs = ['D:\\Goa','H:\\ProjectImageMining\\nups']

#new_dirs = dirs + [os.path.join(initial_path,f) for f in os.listdir(initial_path)]

#for i in dirs:
#    create_features(i)
    
#a = query_image('H:\\ProjectImageMining\\Images\\n02097130-giant_schnauzer\\n02097130_262.jpg')   
"""
fea,ims = create_features("C:\Users\Prashant\Desktop\Proj_Img_Min\WebService\imgmining\static\DB\Exp_data_1")
res = result(fea,ims)
res_1 = req_result(fea,ims,"Exp_data_1//019.JPG")
print name
print value

from fhl import *
fea,ims = create_features("Exp_data_1")
res = result(fea,ims)
nfea,nims = add_image(fea,"new",ims)
nres = result(nfea,nims)
"""
