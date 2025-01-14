# Absolute path: C:\_YHJ\fast\backend\ml\models\xgb\xg_model.py

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from ml.common.data_processing import split_data
from ml.common.model_evaluation import evaluate_model_performance
from ml.common.file_operations import save_model, load_model, save_data_to_csv

class XGModel:
    def __init__(self):
        self.model = None
        self.X_processed = None
        self.y_processed = None
        self.id_material = None
        self.X_test = None
        self.y_test = None
        self.id_material_test = None
        self.features = None
        self.target_column = 'Defect_Flag'

    def load_data_and_train_model(self, X, y, id_material, **model_params):
        try:
            self.X_processed = X
            self.y_processed = y
            self.id_material = id_material
            self.features = X.columns
            
            X_train, self.X_test, y_train, self.y_test, id_material_train, self.id_material_test = split_data(
                self.X_processed, self.y_processed, self.id_material)

            # 클래스 불균형 처리
            pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])

            # 기본 모델 파라미터 설정
            default_params = {
                'n_estimators': 100,
                'max_depth': 3,
                'learning_rate': 0.1,
                'random_state': 42,
                'n_jobs': -1,
                'scale_pos_weight': pos_weight
            }

            # JSON에서 전달된 파라미터로 기본 파라미터 업데이트
            default_params.update(model_params)

            # 모델 생성 및 학습
            self.model = XGBClassifier(**default_params)
            self.model.fit(X_train, y_train)

            print(f"Number of samples in training set: {len(X_train)}")
            print(f"Number of samples in test set: {len(self.X_test)}")
        except Exception as e:
            print(f"An error occurred while loading data and training model: {e}")
            raise

    def predict(self, input_data):
        return self.model.predict(input_data)

    def get_model_performance(self):
        try:
            return evaluate_model_performance(self.model, self.X_test, self.y_test)
        except Exception as e:
            print(f"An error occurred while getting model performance: {e}")
            raise

    def get_feature_importance(self):
        try:
            importance = self.model.feature_importances_
            importance = 100.0 * (importance / importance.max())
            return dict(sorted(zip(self.features, importance), key=lambda x: x[1], reverse=True))
        except Exception as e:
            print(f"An error occurred while getting feature importance: {e}")
            raise

    def save_processed_data_to_csv(self, output_path):
        try:
            processed_data = pd.concat([self.id_material, self.X_processed], axis=1)
            processed_data['actual_target'] = self.y_processed
            processed_data['predicted_target'] = self.predict(self.X_processed)
            save_data_to_csv(processed_data, output_path)
        except Exception as e:
            print(f"An error occurred while saving processed data to CSV: {e}")
            raise

    def save_model(self, file_path):
        """Save the trained model to a file."""
        try:
            save_model(self.model, file_path)
        except Exception as e:
            print(f"An error occurred while saving the model: {e}")
            raise

    def load_model(self, file_path):
        """Load a model from a file."""
        try:
            self.model = load_model(file_path)
        except Exception as e:
            print(f"An error occurred while loading the model: {e}")
            raise
