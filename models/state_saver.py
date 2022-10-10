from queue import Queue
from models.helper_functions import create_actions, fill_default_key_conf, get_updated_config_model, get_config
from models.dnn_model import REBUFFER_INDEX, DNN
import torch
from models.ae_trainer import train_ae
import numpy as np
from models.dnn_model import REBUFFER_INDEX

#TODO: add state_saver_size, state_saver_max_bin, state_path to talents
class StateSaver:
    def __init__(self, num_clients, config, helper_model):
        self.num_clients = num_clients
        self.prediction_model = helper_model

        self.bin_size = fill_default_key_conf(model_config, 'state_saver_size')
        self.max_bins = fill_default_key_conf(model_config, 'state_saver_max_bin')
        self.state_path = fill_default_key_conf(config, 'state_path')

        self.states = [open(f'{self.state_path}/states_{i}', 'w') for i in range(num_clients)]
        self.qoes = [open(f'{self.state_path}/qoes_{i}', 'w') for i in range(num_clients)]

        self.training = not get_config()['test']
        self.mapping_actions = {cc: np.arange(self.num_actions) == i for i, cc in enumerate(get_config()['ccs'])}
        print('created StateSaver')

    def predict(self, state):
        return self.prediction_model.predict(state)

    def update(self, state):
        if not self.training:
            return
        output[0, REBUFFER_INDEX] /= get_config()['buffer_length_coef']
        output[0, REBUFFER_INDEX] = self.discretize_output(output[0, REBUFFER_INDEX])
        output[0, :REBUFFER_INDEX] /= 30.0
        qoe_vec = output.reshape(-1)
        state_ = np.array(state['qoe_state']).reshape(-1)
        self.states[state['server_id']].write(','.join(str(val) for val in state_) + '\n')
        self.states[state['server_id']].flush()

        self.qoes[state['server_id']].write(','.join(str(val) for val in qoe) + '\n')
        self.qoes[state['server_id']].flush()

    def discretize_output(self, raw_out):
        # z = np.array(raw_out)
        z = torch.floor((raw_out + 0.5 * self.bin_size) / self.bin_size )
        return torch.clamp(z, min=0, max=self.max_bins)
        

    def clear(self):
        self.states[state['server_id']].flush()
        self.qoes[state['server_id']].flush()

    def save(self):
        if self.model is not None:
            self.model.save()

    def load(self):
        self.prediction_model.load()
        print('loaded StateSaver')
    
    def done(self):
        self.save()

    def update_helper_model(self, helper_model):
        self.prediction_model = helper_model
        self.load()