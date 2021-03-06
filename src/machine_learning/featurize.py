#Created By: Logan Fillo
#Created On: 2020-03-12

import numpy as np
import cv2 as cv


"""
Functions used to featurize object data for training and classification
"""


class PoleFeaturizer:
    """
    A class for constructing pole features for building models and classification
    """


    def __init__(self):
        self.cnt_features = ContourFeatures()


    def featurize_for_training(self, data):
        """
        Featurizes the model data given in the form of a list of convex hull/label tuples
        and returns the feature array and label vector

        @param data: A list of tuples where each tuple is (convex hull, 1 if hull is pole, 0 otherwise)

        @returns: The feature matrix X, and label vector y used for training models
        """
        X = []
        y = []
        
        for d in data:
            hull, label = d
            X.append(self.form_feature_vector(hull))
            y.append(label)
        
        return np.asarray(X).astype(float), np.asarray(y).astype(float)


    def featurize_for_classification(self, hulls):
        """
        Featurizes the hulls and returns the features matrix X_hat

        @param hulls: The convex hulls to be featurized

        @returns: The feature matrix X_hat
        """
        X_hat = []  
        for hull in hulls:
            X_hat.append(self.form_feature_vector(hull))    
        return np.asarray(X_hat).astype(float)


    def form_feature_vector(self, hull):
        """
        Forms the feature vector from a convex hull

        @param hull: The convex hull to featurize

        @returns: The feature vector of the hull
        """
        features = []

        MA, ma, angle = self.cnt_features.ellispe_features(hull)
        hull_area, rect_area, aspect_ratio = self.cnt_features.area_features(hull)
        hu_moments = self.cnt_features.hu_moments_features(hull)

        axis_ratio = float(MA)/ma
        angle = np.abs(np.sin(angle *np.pi/180))
        extent = rect_area/hull_area

        features.append(axis_ratio)
        features.append(aspect_ratio)
        features.append(extent)
        features.append(angle)
        features += hu_moments

        return np.asarray(features).astype(float)


class ContourFeatures:
    """
    A class for contour features
    """
    
    
    def ellispe_features(self,cnt):
        """
        Produces ellipse features of the cnt

        @param cnt: A convex hull contour 
        
        @returns: The major axis (MA), minor axis (ma) and angle of contour
        """
        angle = 0
        MA = 1
        ma = 1
        try:    
            # Fit ellipse only works if convex hull has 3 points
            (x,y),(MA,ma),angle = cv.fitEllipse(cnt)
        except:
            pass
        return MA, ma, angle


    def area_features(self,cnt):
        """
        Produces area features of the contour

        @param cnt: A convex hull contour
        
        @returns: The contour area, bounding rect area, aspect ratio
        """

        cnt_area = cv.contourArea(cnt)
        x,y,w,h = cv.boundingRect(cnt)
        rect_area = w*h
        aspect_ratio =  float(w)/h
        return cnt_area, rect_area, aspect_ratio


    def hu_moments_features(self,cnt):
        """
        Produces the hu moment features of the contour

        @param cnt: A convex hull contour

        @returns: A list of the 7 hu moments
        """
        moments = cv.moments(cnt)
        hu_moments = cv.HuMoments(moments)

        return list(hu_moments.flatten())
