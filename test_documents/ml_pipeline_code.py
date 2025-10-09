"""
Technical Documentation: Machine Learning Pipeline Architecture
Version 2.1 - Production System
Date: October 9, 2025
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import logging
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import asyncio
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import torch
import torch.nn as nn
import torch.optim as optim

class MLPipelineConfig:
    """Configuration management for ML pipeline"""

    def __init__(self):
        self.model_configs = {
            "random_forest": {
                "n_estimators": 100,
                "max_depth": 10,
                "min_samples_split": 5,
                "random_state": 42
            },
            "gradient_boosting": {
                "n_estimators": 100,
                "learning_rate": 0.1,
                "max_depth": 6,
                "random_state": 42
            },
            "neural_network": {
                "hidden_layers": [128, 64, 32],
                "dropout_rate": 0.3,
                "learning_rate": 0.001,
                "batch_size": 32,
                "epochs": 100
            }
        }

        self.data_processing = {
            "missing_value_strategy": "median",
            "outlier_detection": "iqr",
            "feature_scaling": "standard",
            "categorical_encoding": "label"
        }

        self.validation = {
            "test_size": 0.2,
            "cv_folds": 5,
            "random_state": 42,
            "stratify": True
        }

class DataProcessor:
    """Advanced data processing and feature engineering"""

    def __init__(self, config: MLPipelineConfig):
        self.config = config
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []

    def preprocess_data(self, df: pd.DataFrame, target_column: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Comprehensive data preprocessing pipeline

        Args:
            df: Input dataframe
            target_column: Name of target variable column

        Returns:
            Processed features and target arrays
        """
        logging.info(f"Starting data preprocessing for {len(df)} samples")

        # Separate features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]

        # Handle missing values
        X = self._handle_missing_values(X)

        # Detect and handle outliers
        X = self._handle_outliers(X)

        # Encode categorical variables
        X = self._encode_categorical_features(X)

        # Feature scaling
        X = self._scale_features(X)

        # Feature selection
        X = self._select_features(X, y)

        # Store feature names
        self.feature_names = list(X.columns) if hasattr(X, 'columns') else [f"feature_{i}" for i in range(X.shape[1])]

        logging.info(f"Preprocessing complete. Final feature count: {X.shape[1]}")

        return X.values, y.values

    def _handle_missing_values(self, X: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values based on configuration"""
        strategy = self.config.data_processing["missing_value_strategy"]

        for column in X.columns:
            if X[column].dtype in ['int64', 'float64']:
                if strategy == "median":
                    X[column].fillna(X[column].median(), inplace=True)
                elif strategy == "mean":
                    X[column].fillna(X[column].mean(), inplace=True)
                else:
                    X[column].fillna(0, inplace=True)
            else:
                X[column].fillna(X[column].mode()[0] if not X[column].mode().empty else "unknown", inplace=True)

        return X

    def _handle_outliers(self, X: pd.DataFrame) -> pd.DataFrame:
        """Detect and handle outliers using IQR method"""
        if self.config.data_processing["outlier_detection"] == "iqr":
            for column in X.select_dtypes(include=[np.number]).columns:
                Q1 = X[column].quantile(0.25)
                Q3 = X[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                # Cap outliers
                X[column] = np.clip(X[column], lower_bound, upper_bound)

        return X

    def _encode_categorical_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features"""
        for column in X.select_dtypes(include=['object']).columns:
            if column not in self.encoders:
                self.encoders[column] = LabelEncoder()
                X[column] = self.encoders[column].fit_transform(X[column].astype(str))
            else:
                X[column] = self.encoders[column].transform(X[column].astype(str))

        return X

    def _scale_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Scale numerical features"""
        numerical_columns = X.select_dtypes(include=[np.number]).columns

        if len(numerical_columns) > 0:
            if 'scaler' not in self.scalers:
                self.scalers['scaler'] = StandardScaler()
                X[numerical_columns] = self.scalers['scaler'].fit_transform(X[numerical_columns])
            else:
                X[numerical_columns] = self.scalers['scaler'].transform(X[numerical_columns])

        return X

    def _select_features(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """Feature selection based on importance"""
        # For now, return all features
        # In production, implement feature selection algorithms
        return X

class ModelTrainer:
    """Advanced model training and evaluation"""

    def __init__(self, config: MLPipelineConfig):
        self.config = config
        self.models = {}
        self.best_model = None
        self.best_score = 0

    def train_ensemble_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Train multiple models and create ensemble

        Args:
            X: Feature matrix
            y: Target vector

        Returns:
            Training results and model performance
        """
        results = {}

        # Train Random Forest
        rf_model = self._train_random_forest(X, y)
        results['random_forest'] = self._evaluate_model(rf_model, X, y)

        # Train Gradient Boosting
        gb_model = self._train_gradient_boosting(X, y)
        results['gradient_boosting'] = self._evaluate_model(gb_model, X, y)

        # Train Neural Network
        nn_model = self._train_neural_network(X, y)
        results['neural_network'] = self._evaluate_model(nn_model, X, y)

        # Select best model
        self._select_best_model(results)

        return results

    def _train_random_forest(self, X: np.ndarray, y: np.ndarray) -> RandomForestClassifier:
        """Train Random Forest model with hyperparameter tuning"""
        rf_config = self.config.model_configs["random_forest"]

        # Hyperparameter grid
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15, None],
            'min_samples_split': [2, 5, 10]
        }

        rf = RandomForestClassifier(**rf_config)

        # Grid search for best parameters
        grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
        grid_search.fit(X, y)

        best_model = grid_search.best_estimator_
        self.models['random_forest'] = best_model

        logging.info(f"Random Forest trained. Best params: {grid_search.best_params_}")

        return best_model

    def _train_gradient_boosting(self, X: np.ndarray, y: np.ndarray) -> GradientBoostingRegressor:
        """Train Gradient Boosting model"""
        gb_config = self.config.model_configs["gradient_boosting"]

        gb = GradientBoostingRegressor(**gb_config)
        gb.fit(X, y)

        self.models['gradient_boosting'] = gb

        logging.info("Gradient Boosting model trained successfully")

        return gb

    def _train_neural_network(self, X: np.ndarray, y: np.ndarray):
        """Train deep neural network using TensorFlow"""
        nn_config = self.config.model_configs["neural_network"]

        # Build model architecture
        model = Sequential()

        # Input layer
        model.add(Dense(nn_config["hidden_layers"][0],
                       activation='relu',
                       input_shape=(X.shape[1],)))
        model.add(Dropout(nn_config["dropout_rate"]))

        # Hidden layers
        for units in nn_config["hidden_layers"][1:]:
            model.add(Dense(units, activation='relu'))
            model.add(Dropout(nn_config["dropout_rate"]))

        # Output layer
        if len(np.unique(y)) == 2:
            model.add(Dense(1, activation='sigmoid'))
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        else:
            model.add(Dense(len(np.unique(y)), activation='softmax'))
            model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        # Train model
        history = model.fit(X, y,
                          epochs=nn_config["epochs"],
                          batch_size=nn_config["batch_size"],
                          validation_split=0.2,
                          verbose=0)

        self.models['neural_network'] = model

        logging.info("Neural network trained successfully")

        return model

    def _evaluate_model(self, model, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance"""
        try:
            if hasattr(model, 'predict_proba'):
                # Classification model
                scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
                predictions = model.predict(X)
                precision, recall, f1, _ = precision_recall_fscore_support(y, predictions, average='weighted')

                return {
                    'accuracy': scores.mean(),
                    'accuracy_std': scores.std(),
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1
                }
            else:
                # TensorFlow model or regression
                if hasattr(model, 'evaluate'):
                    # TensorFlow model
                    loss, accuracy = model.evaluate(X, y, verbose=0)
                    return {
                        'accuracy': accuracy,
                        'loss': loss,
                        'precision': 0.0,  # Would need separate calculation
                        'recall': 0.0,
                        'f1_score': 0.0
                    }
                else:
                    # Regression model
                    from sklearn.metrics import mean_squared_error, r2_score
                    predictions = model.predict(X)
                    mse = mean_squared_error(y, predictions)
                    r2 = r2_score(y, predictions)

                    return {
                        'mse': mse,
                        'rmse': np.sqrt(mse),
                        'r2_score': r2,
                        'accuracy': r2  # Use R² as accuracy for regression
                    }
        except Exception as e:
            logging.error(f"Error evaluating model: {e}")
            return {'accuracy': 0.0, 'error': str(e)}

    def _select_best_model(self, results: Dict[str, Dict[str, float]]):
        """Select the best performing model"""
        best_accuracy = 0
        best_model_name = None

        for model_name, metrics in results.items():
            accuracy = metrics.get('accuracy', 0)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_model_name = model_name

        if best_model_name:
            self.best_model = self.models[best_model_name]
            self.best_score = best_accuracy
            logging.info(f"Best model: {best_model_name} (Accuracy: {best_accuracy:.4f})")

class MLPipeline:
    """Main ML Pipeline orchestrator"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = MLPipelineConfig()
        self.data_processor = DataProcessor(self.config)
        self.model_trainer = ModelTrainer(self.config)
        self.pipeline_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'ml_pipeline_{self.pipeline_id}.log'),
                logging.StreamHandler()
            ]
        )

    async def run_pipeline(self, data_path: str, target_column: str) -> Dict[str, Any]:
        """
        Execute the complete ML pipeline

        Args:
            data_path: Path to training data
            target_column: Target variable column name

        Returns:
            Pipeline execution results
        """
        logging.info(f"Starting ML Pipeline {self.pipeline_id}")

        try:
            # Load data
            logging.info(f"Loading data from {data_path}")
            df = pd.read_csv(data_path)

            # Data validation
            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' not found in data")

            # Preprocess data
            X, y = self.data_processor.preprocess_data(df, target_column)

            # Train models
            training_results = self.model_trainer.train_ensemble_models(X, y)

            # Generate pipeline report
            pipeline_report = self._generate_pipeline_report(df, training_results)

            # Save results
            self._save_pipeline_results(pipeline_report)

            logging.info("ML Pipeline completed successfully")

            return pipeline_report

        except Exception as e:
            logging.error(f"Pipeline failed: {e}")
            raise e

    def _generate_pipeline_report(self, df: pd.DataFrame, training_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive pipeline report"""

        report = {
            "pipeline_id": self.pipeline_id,
            "execution_timestamp": datetime.now().isoformat(),
            "data_summary": {
                "total_samples": len(df),
                "total_features": len(df.columns) - 1,
                "missing_values": df.isnull().sum().sum(),
                "data_types": df.dtypes.value_counts().to_dict()
            },
            "preprocessing_summary": {
                "final_feature_count": len(self.data_processor.feature_names),
                "feature_names": self.data_processor.feature_names,
                "scalers_used": list(self.data_processor.scalers.keys()),
                "encoders_used": list(self.data_processor.encoders.keys())
            },
            "model_results": training_results,
            "best_model": {
                "name": type(self.model_trainer.best_model).__name__ if self.model_trainer.best_model else None,
                "accuracy": self.model_trainer.best_score
            },
            "recommendations": self._generate_recommendations(training_results)
        }

        return report

    def _generate_recommendations(self, training_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []

        best_accuracy = max([result.get('accuracy', 0) for result in training_results.values()])

        if best_accuracy < 0.8:
            recommendations.append("Consider collecting more training data")
            recommendations.append("Review feature engineering strategies")
            recommendations.append("Explore advanced ensemble methods")

        if best_accuracy > 0.95:
            recommendations.append("Check for potential overfitting")
            recommendations.append("Validate on external test set")

        # Model-specific recommendations
        for model_name, results in training_results.items():
            accuracy = results.get('accuracy', 0)
            if accuracy == best_accuracy:
                recommendations.append(f"Deploy {model_name} as primary model")

        return recommendations

    def _save_pipeline_results(self, report: Dict[str, Any]):
        """Save pipeline results to file"""
        filename = f"pipeline_report_{self.pipeline_id}.json"

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logging.info(f"Pipeline report saved to {filename}")

# Usage example and testing
async def main():
    """Main function for testing the ML pipeline"""

    # Create sample data for testing
    np.random.seed(42)

    # Generate synthetic dataset
    n_samples = 1000
    n_features = 10

    X_synthetic = np.random.randn(n_samples, n_features)
    y_synthetic = (X_synthetic[:, 0] + X_synthetic[:, 1] * 0.5 + np.random.randn(n_samples) * 0.1) > 0

    # Create DataFrame
    columns = [f"feature_{i}" for i in range(n_features)] + ["target"]
    df_synthetic = pd.DataFrame(
        np.column_stack([X_synthetic, y_synthetic.astype(int)]),
        columns=columns
    )

    # Save synthetic data
    df_synthetic.to_csv("synthetic_ml_data.csv", index=False)

    # Initialize and run pipeline
    pipeline = MLPipeline()
    results = await pipeline.run_pipeline("synthetic_ml_data.csv", "target")

    print("\n=== ML Pipeline Results ===")
    print(f"Pipeline ID: {results['pipeline_id']}")
    print(f"Best Model: {results['best_model']['name']}")
    print(f"Best Accuracy: {results['best_model']['accuracy']:.4f}")
    print("\nRecommendations:")
    for rec in results['recommendations']:
        print(f"- {rec}")

if __name__ == "__main__":
    asyncio.run(main())

"""
Performance Optimization Notes:

1. Memory Management:
   - Use data generators for large datasets
   - Implement batch processing for feature engineering
   - Clear unused variables explicitly

2. Computation Optimization:
   - Parallelize cross-validation using joblib
   - Use GPU acceleration for neural networks
   - Implement caching for expensive operations

3. Model Selection:
   - Implement early stopping for neural networks
   - Use randomized search for large hyperparameter spaces
   - Consider automated ML (AutoML) frameworks

4. Production Deployment:
   - Implement model versioning
   - Add model monitoring and drift detection
   - Create REST API endpoints for predictions
   - Implement A/B testing framework

5. Scalability Considerations:
   - Use distributed computing (Spark/Dask) for large datasets
   - Implement streaming predictions
   - Consider cloud-based ML platforms
   - Add horizontal scaling capabilities
"""
