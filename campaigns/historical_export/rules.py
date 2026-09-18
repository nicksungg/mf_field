"""Small readable decision trees; leaf mixtures fit actual combined field error."""
import numpy as np
from sklearn.tree import DecisionTreeRegressor, export_text
from mixture import simplex_fit,sample_balance,balanced_score

def rule_inputs(x,classes,metadata,class_order,feature_names,model_names):
    onehot=np.asarray([[float(c==cc) for cc in class_order] for c in classes])
    flat=x.reshape(len(x),-1)
    names=[m+':'+f for m in model_names for f in feature_names]
    return np.concatenate([onehot,metadata,flat],axis=1), ['class:'+c for c in class_order]+[
        'log_hf_grid_h','log_hf_grid_w','log_lf_grid_h','log_lf_grid_w','log_hf_training_count','condition_dimension']+names

def fit_rules(x,g,prior,d,c,xt,gt,pt,dt,ct,names):
    base_score=balanced_score(pt,gt,dt,ct)
    best=dict(tree=None,leaves={},alpha=0.,tune_score=base_score,text='Use the available dataset/class/global prior.')
    importance=sample_balance(d,c)
    scales={dd:max(float(np.trace(g[np.asarray(d)==dd],axis1=1,axis2=2).mean()/g.shape[1]),1e-24) for dd in np.unique(d)}
    opt_weight=importance/np.asarray([scales[dd] for dd in d])
    target=np.log(np.maximum(np.diagonal(g,axis1=1,axis2=2),1e-24))
    target-=target.mean(axis=1,keepdims=True)
    for depth in (1,2,3):
        tree=DecisionTreeRegressor(max_depth=depth,min_samples_leaf=max(12,int(np.sqrt(len(x)))),random_state=0)
        tree.fit(x,target,sample_weight=importance)
        leaf_id=tree.apply(x);leaves={int(k):simplex_fit(g[leaf_id==k],opt_weight[leaf_id==k]) for k in np.unique(leaf_id)}
        wt=np.asarray([leaves[int(k)] for k in tree.apply(xt)])
        for alpha in (.25,.5,1.):
            score=balanced_score((1-alpha)*pt+alpha*wt,gt,dt,ct)
            if score<best['tune_score']-1e-12:
                best=dict(tree=tree,leaves=leaves,alpha=alpha,tune_score=score,depth=depth,
                          text=export_text(tree,feature_names=names,decimals=4))
    return best

def predict_rules(rule,x,prior):
    if rule['tree'] is None:return prior.copy()
    w=np.asarray([rule['leaves'][int(k)] for k in rule['tree'].apply(x)])
    return (1-rule['alpha'])*prior+rule['alpha']*w

