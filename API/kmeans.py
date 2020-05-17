from sklearn.cluster import KMeans
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def rearrangecontent(allusers):
    dataf = pd.DataFrame(allusers).T.head(200)
    datan = pd.DataFrame(allusers).T
    names_dict = dict(zip(datan.screen_name, datan.group))
    print(len(names_dict))
    
    links = dataf[['screen_name', 'mentioned', 'weight']].copy().T.to_dict()
    links_mentions = dataf[['screen_name', 'mentioned', 'weight']].iloc[:,1]
    links_sn = dataf[['screen_name', 'mentioned', 'weight']].iloc[:,0]
    links_nodes = links_mentions.append(links_sn).unique().tolist()
    nodes = {}
    s = 0
    for iSN in range(len(links_nodes)):
        if links_nodes[iSN] in names_dict:
            temp_obj = {}
            temp_obj['screen_name'] = links_nodes[iSN]
            temp_obj['group'] = names_dict[links_nodes[iSN]]
            nodes[iSN] = temp_obj
            s=s +1
    
    print(len(links_nodes), s)

    final = {}
    final['nodes'] = nodes
    final['links'] = links
    return final


def clusterusersbyscore(allusers):
    dataf = pd.DataFrame(allusers).T
    #mdataf = dataf[dataf.mentioned != 0 & (dataf.weight > 0)].copy()
    km = KMeans(n_clusters=5)
    y_predicted = km.fit_predict(dataf[['score' , 'weight']])
    dataf['group']=y_predicted
    final_df = dataf.sort_values(by=['weight'], ascending=False)
    return rearrangecontent(final_df.T.to_dict())

