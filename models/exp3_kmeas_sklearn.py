from config_creator import CONFIG
from models.helper_functions import get_updated_config_model, fill_default_key, fill_default_key_conf, merge_state_actions, create_actions
from models.exp3 import Exp3
from models.helper_functions import get_config
import numpy as np
import time
import json
import pickle

#TODO: add sklearn_predictors_path to talents
class SklearnMorpheus:
    def __init__(self, num_clients, model_config):
        self.predictors_path =  fill_default_key_conf(model_config, 'sklearn_predictors_path')
        self.qoe_predictor = pickle.load(f'{self.predictors_path}/qoe.pkl')
        self.rebuffer_predictor = pickle.load(f'{self.predictors_path}/rebuffer.pkl')
        self.actions = create_actions()
        self.num_clusters = int(len(self.actions) ** 3) + len(self.actions)
        self.cluster_name = fill_default_key(model_config, 'cluster_name', f"clusters_{self.context_model.context_type}_{get_config()['abr']}_{self.num_clusters}_{context_layers}")

        exp3_config = get_updated_config_model('exp3', model_config)
        save_name = fill_default_key(model_config, 'save_name', f"exp3_{self.cluster_name[len('clusters_'):]}_scoring_{get_config()['buffer_length_coef']}")
        self.exp3_contexts = [Exp3(num_clients, exp3_config) for _ in range(self.num_clusters)]
        for i in range(self.num_clusters):
            path = fill_default_key_conf(model_config, 'exp3_model_path')
            self.exp3_contexts[i].save_path = f"{path}{save_name}_{i}.npy"
        print('created sklearnMorpheus')
    
    def get_cluster_id(self, x):
        x = self.to_numpy(x)
        ssims, rebuffers = [], []
        for action in self.actions:
            ssims.append(self.qoe_predictor.predict(merge_state_actions(x, action)).reshape(-1))
            rebuffers.append(self.rebuffer_predictor.predict(merge_state_actions(x, action)).reshape(-1))
        ssims, rebuffers = np.array(ssims), np.array(rebuffers)
        max_ssim = np.argmax(ssims)
        max_rebuffer = np.argmax(rebuffers)
        min_rebuffer = np.argmin(rebuffers)
        if context_action[max_rebuffer, REBUFFER_INDEX] <= 0: #no rebuffer:
            max_rebuffer = self.num_actions
            min_rebuffer = 0
        return int(max_rebuffer * self.num_actions * self.num_actions + min_rebuffer * self.num_actions + max_ssim)

    def predict(self, state):
        id_ = self.get_cluster_id(state['state'])
        return self.exp3_contexts[id_].predict(state)

    def update(self, state):
        id_ = self.get_cluster_id(state['state'])
        self.exp3_contexts[id_].update(state)

    def save_json(self):
        if CONFIG['test']:
            return

    def clear(self):
        for exp3 in self.exp3_contexts:
            exp3.clear()

    def save(self):
        for exp3 in self.exp3_contexts:
            exp3.save()

    def load(self):
        for exp3 in self.exp3_contexts:
            exp3.load()
        print('loaded sklearnMorpheus')

    def done(self):
        self.save()