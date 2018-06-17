import numpy as np
import copy
import warnings

class clustering():
    def __init__(self, data, NGroups, MaxL, MinGroupSize, xStd):
        self.data = data
        self.NGroups = NGroups
        self.MaxL = MaxL
        self.MinGroupSize = MinGroupSize
        self.xStd = xStd
        self.shape = data.shape
        self.avg = np.nanmean(self.data, axis = 0)
        self.data_len = np.sqrt(np.nansum(self.data ** 2, axis = 1))

        # Geef elk categorie een random cluster groep
        if self.shape[0] < self.NGroups:
            groupLst = list(range(self.shape[1]))
        else:
            groupLst = list(range(self.NGroups)) * (self.shape[0]//self.NGroups) + [0] * (self.shape[0] % self.NGroups)
        groupLst = np.array(groupLst).reshape(self.shape[0], 1) 
        self.data = np.concatenate((self.data, groupLst), axis = 1)

        # initial values voor de het gemiddelde van de group
        self.GroupAvg = np.full((self.NGroups, self.shape[1]), 10, dtype=np.float32) 
        self.NewGroupAvg = np.full((self.NGroups, self.shape[1]), 0, dtype=np.float32) 
    
    def Clustering(self):
        """
        cluster de data aan de hand van Euclidean distance (variance wordt eigenlijk berekend maar dat is distance squared).

        algoritme is als volgt:
        neem van elk cluster het gemiddelde. 
        Als het gemiddelde op een datum nan is neem het gemiddelde van alle data.
        bereken de afstand van elk datapunt tot dat gemiddelde en sla dat op in datacube.
        Zoek vervolgens voor elk datapunt de kortste afstand tot 1 van de gemiddelde en
        dit wordt de nieuwe cluster groep voor het datapunt.
        """
        self.GroupAvg = copy.deepcopy(self.NewGroupAvg)
        DataCube = np.empty((self.shape[0], self.NGroups, 2),dtype=np.float32)
        for cluster in range(self.NGroups): 
            print(cluster)
            Cluster = self.data[np.where(self.data[:,-1] == cluster)]
            # nanmean geeft warnings als er alleen maar nans zijn dit onderdrukt het.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                tmp = np.nanmean(Cluster[:,:-1], axis = 0) 
            tmp[np.isnan(tmp)] = self.avg[np.isnan(tmp)]
            self.NewGroupAvg[cluster,:] = tmp
            Distance = np.nansum((self.data[:, :-1] - self.NewGroupAvg[cluster, :])**2, axis = 1)
            DataCube[:,cluster,:] = np.stack((Distance, np.full(self.shape[0], cluster, dtype=np.float32))).T 
        groupLst = np.argmin(DataCube[:, :, 0], axis = 1) 
        self.data[:,-1] = groupLst 

    def Clustering2(self):
        """
        cluster de data aan de hand van cos hoek.

        algoritme is als volgt:
        neem van elk cluster het gemiddelde. 
        Als het gemiddelde op een datum nan is neem het gemiddelde van alle data.
        bereken de hoek van elk datapunt tot dat gemiddelde en sla dat op in datacube.
        Zoek vervolgens voor elk datapunt de kleinste hoek (dichtst bij 1) tot 1 van de gemiddelde en
        dit wordt de nieuwe cluster groep voor het datapunt.
        """
        self.GroupAvg = copy.deepcopy(self.NewGroupAvg)
        DataCube = np.empty((self.shape[0], self.NGroups, 2),dtype=np.float32)
        for cluster in range(self.NGroups): 
            Cluster = self.data[np.where(self.data[:,-1] == cluster)]
            # nanmean geeft warnings als er alleen maar nans zijn dit onderdrukt het.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                tmp = np.nanmean(Cluster[:,:-1], axis = 0) 
            tmp[np.isnan(tmp)] = self.avg[np.isnan(tmp)]
            self.NewGroupAvg[cluster,:] = tmp
            Dot = np.nansum(np.multiply(self.data[:, :-1], self.NewGroupAvg[cluster, :]), axis = 1)
            avg_len = np.sqrt(np.nansum(self.NewGroupAvg[cluster, :] ** 2))
            Cos = Dot / (avg_len * self.data_len)
            DataCube[:,cluster,:] = np.stack((Cos, np.full(self.shape[0], cluster, dtype=np.float32))).T
        groupLst = np.argmax(DataCube[:, :, 0], axis = 1)
        self.data[:,-1] = groupLst

    def ClusterCompare(self):
        self.ChangedClusterAmount = False #keeps track of if clusters are combined 
        StdOfClusters = np.empty((self.NumberOfClusters,self.Shape[2]),dtype=np.float32) #the std of each cluster
        for cluster in range(self.NumberOfClusters): #walks through all the clusters
            Cluster = self.DataArray[np.where(self.DataArray[:,-1] == cluster)] #search for all the datapoints that belong to a cluster and stores them in an new array
            StdOfClusters[cluster,:] = np.std(Cluster[:,:-2],axis=0) #calculated the actual Std of the clusters
        CompareDict = {}
        for cluster in range(self.NumberOfClusters): #walks through all the clusters
            CombineLst = []
            for nextcluster in range(cluster+1,self.NumberOfClusters):
                DiffVectorOfAvg = self.ClusterAvgArray[cluster]-self.ClusterAvgArray[nextcluster] #the difference between the clusters
                DiffUnitVectorOfAvg = DiffVectorOfAvg/(np.sqrt(np.sum(DiffVectorOfAvg**2))) #the difference between the cluster of length 1
                DiffVectorOfAvgLength = np.sqrt(np.sum(DiffVectorOfAvg**2))
                StdAlongUnitVectorlength0 = np.sqrt(np.sum(np.dot(StdOfClusters[cluster],DiffUnitVectorOfAvg)**2))
                StdAlongUnitVectorlength1 = np.sqrt(np.sum(np.dot(StdOfClusters[nextcluster],DiffUnitVectorOfAvg)**2))
                if DiffVectorOfAvgLength < self.xStd*(StdAlongUnitVectorlength1+StdAlongUnitVectorlength0):
                    CombineLst.append(nextcluster)
            CompareDict[cluster] = CombineLst

        clusterLst = [] #The list with which cluster to combine
        cluster = 0
        while cluster < self.NumberOfClusters: #loops through all the current clusters
            if not cluster in [x for sublist in clusterLst for x in sublist]: #if the old cluster is already put in an other cluster it is skipped
                NewCluster = [cluster]+CompareDict[cluster] #the next old cluster and the clusters that are within distance of the cluster are put in a list to combine them
                for AdjacentCluster in CompareDict[cluster]: #checks if the clusters that are combined with cluster have also adjacentclusters
                    self.ChangedClusterAmount = True #if CompareDict[cluster] is not empty at least two clusters are combined
                    NewCluster = NewCluster + CompareDict[AdjacentCluster] #adds the adjacent cluster to the NewCluster
                NewCluster = set(NewCluster) #makes it into a set to remove dubbels
                NewCluster.difference_update(set([x for sublist in clusterLst for x in sublist])) #checks if the clusters that are selected for combining were not already selected
                clusterLst.append(list(NewCluster)) #appens the new list of combining clusters to the list with all the combinations
            cluster += 1

        if self.ChangedClusterAmount: #Update the new clusters with new cluster numbers (to make them have the range(0,self.NumberOfClusters again)
            newcluster = 0
            for clusterlst in clusterLst+[[self.NumberOfClusters]]: 
                for cluster in clusterlst:
                    index = np.where(self.DataArray[:,-1] == cluster) #search for all the datapoints that belong to a cluster and saves the position in the array (index)
                    Cluster = self.DataArray[index] #cuts one cluster out of the DataArray
                    Cluster[:,-1] = newcluster #gives the cluster a new number
                    self.DataArray[index] = Cluster #opposites from before now we use the index to change the data points in the DataArray with a specific cluster number to the numbers that are stored in Cluster (that can be or the left over cluster or the current cluster)
                newcluster += 1
            self.NumberOfClusters = newcluster-1

            #resetting the average and std, because there are new clusters
            self.oldClusterAvgArray = np.full((self.NumberOfClusters,self.Shape[2]),10,dtype=np.float32) #initial values, they are not used in any computations of the algorithm
            self.ClusterAvgArray = np.full((self.NumberOfClusters,self.Shape[2]),0,dtype=np.float32) #initial values, they are not used in any computations of the algorithm