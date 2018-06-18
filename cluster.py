import numpy as np
import copy
import warnings

class clustering():
    def __init__(self, data, NGroups):
        self.data = data
        self.NGroups = NGroups
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
