import pandas as pd
from scipy.stats import zscore, ttest_ind
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import json
from typing import Dict, Any, List, Optional
import os
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

class DataCleaningTool:
    """
    Tool for cleaning and preprocessing data.
    Provides methods for handling missing values and removing outliers.
    """
    def __init__(self, name: str = "DataCleaningTool"):
        self.name = name

    def handle_missing_values(self, data: pd.DataFrame, strategy: str = 'mean', value=None, fields: Optional[List[str]] = None, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Handles missing values using different strategies.
        
        Parameters:
            data: The DataFrame to process
            strategy: Strategy to use ('mean', 'median', 'mode', or 'constant')
            value: Value to use when strategy is 'constant'
            fields: List of column names to process (defaults to all columns)
            columns: Alternative name for fields parameter (for backward compatibility)
        """
        # Create a copy to avoid modifying the original
        result = data.copy()
        
        # Determine which columns to process (allow both 'fields' and 'columns' parameters)
        columns_to_process = columns if columns is not None else fields
        columns_to_process = columns_to_process if columns_to_process is not None else data.columns
        
        # Filter to only include columns that actually exist in the data
        columns_to_process = [col for col in columns_to_process if col in data.columns]
        
        if not columns_to_process:
            return result  # No valid columns to process
            
        if strategy == 'mean':
            # Only apply mean to numeric columns
            numeric_cols = [col for col in columns_to_process if col in data.select_dtypes(include=['number']).columns]
            if numeric_cols:
                for col in numeric_cols:
                    result[col] = result[col].fillna(result[col].mean())
        elif strategy == 'median':
            # Only apply median to numeric columns
            numeric_cols = [col for col in columns_to_process if col in data.select_dtypes(include=['number']).columns]
            if numeric_cols:
                for col in numeric_cols:
                    result[col] = result[col].fillna(result[col].median())
        elif strategy == 'mode':
            # Mode can be applied to any column type
            for col in columns_to_process:
                mode_value = result[col].mode()
                if not mode_value.empty:
                    result[col] = result[col].fillna(mode_value.iloc[0])
        elif strategy == 'constant':
            # Constant can be applied to any column
            for col in columns_to_process:
                result[col] = result[col].fillna(value)
        
        return result

    def remove_outliers_zscore(self, data: pd.DataFrame, threshold: float = 3.0, fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Removes outliers using the Z-score method.
        
        Parameters:
            data: The DataFrame to process
            threshold: Z-score threshold for identifying outliers (default: 3.0)
            fields: List of column names to check for outliers (defaults to all numeric columns)
        """
        result = data.copy()
        
        # Determine which columns to process
        if fields is None:
            numeric_cols = data.select_dtypes(include=['number']).columns
        else:
            numeric_cols = [col for col in fields if col in data.select_dtypes(include=['number']).columns]
        
        if numeric_cols:
            # Apply zscore transformation to each numeric column separately
            for col in numeric_cols:
                # Handle potential NaN values by using 'omit' policy
                result[f"zscore_{col}"] = zscore(result[col].fillna(result[col].mean()), nan_policy='omit')
            
            # Create a mask for rows to keep (where all z-scores are below threshold)
            mask = True
            for col in numeric_cols:
                mask = mask & (result[f"zscore_{col}"].abs() < threshold)
            
            # Apply the mask to filter rows
            result = result[mask]
            
            # Drop the temporary zscore columns
            for col in numeric_cols:
                result = result.drop(f"zscore_{col}", axis=1)
        
        return result # type: ignore

class MLTool:
    """
    Tool for basic machine learning tasks.
    Provides methods for linear regression and k-means clustering.
    """
    def __init__(self, name: str = "MLTool"):
        self.name = name

    def linear_regression(self, data: pd.DataFrame, feature_cols: list, target_col: str) -> dict:
        """Performs linear regression and returns model metrics."""
        X = data[feature_cols]
        y = data[target_col]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        return {
            "coefficients": model.coef_.tolist(),
            "intercept": model.intercept_,
            "r2_score": r2_score(y_test, y_pred),
            "mse": mean_squared_error(y_test, y_pred)
        }

    def kmeans_clustering(self, data: pd.DataFrame, feature_cols: list, n_clusters: int = 3) -> dict:
        """Performs k-means clustering and returns cluster labels."""
        X = data[feature_cols]
        
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        model.fit(X)
        
        return {
            "labels": model.labels_.tolist(),
            "cluster_centers": model.cluster_centers_.tolist()
        }

class ReportingTool:
    """
    Tool for generating summary reports from analysis results.
    """
    def __init__(self, name: str = "ReportingTool", output_dir: str = "reports"):
        self.name = name
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_markdown_report(self, summary: str, results: List[Dict[str, Any]]) -> str:
        """Generates a comprehensive markdown report from a list of results."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.output_dir, f"report_{timestamp}.md")

        md = f"# Analysis Report\n\n## Executive Summary\n{summary}\n\n"
        
        for result in results:
            md += f"## {result.get('title', 'Analysis Step')}\n"
            md += f"**Tool Used**: `{result.get('tool', 'N/A')}`\n\n"
            
            content = result.get('content')
            if isinstance(content, str) and content.startswith('charts/'): # Path to a saved chart
                md += f"![Visualization]({os.path.abspath(content)})\n\n"
            elif isinstance(content, dict):
                md += "```json\n"
                md += json.dumps(content, indent=4)
                md += "\n```\n\n"
            elif isinstance(content, pd.DataFrame):
                 md += content.to_markdown() + "\n\n"
            else:
                md += f"```\n{str(content)}\n```\n\n"
                
        with open(file_path, 'w') as f:
            f.write(md)
        
        return file_path

class StatisticsTool:
    """
    Tool for performing statistical analysis on data.
    Provides methods for descriptive statistics, correlation, and hypothesis testing.
    """
    def __init__(self, name: str = "StatisticsTool"):
        self.name = name

    def describe(self, data: pd.DataFrame) -> Dict:
        """Generates descriptive statistics."""
        return data.describe().to_dict()

    from typing import Literal

    def correlation(self, data: pd.DataFrame, method: Literal['pearson', 'kendall', 'spearman'] = 'pearson') -> Dict:
        """Calculates pairwise correlation of columns."""
        numeric_df = data.select_dtypes(include=['number'])
        return numeric_df.corr(method=method).to_dict()

    def t_test(self, data: pd.DataFrame, group_col: str, value_col: str) -> dict:
        """Performs an independent t-test on two groups in a dataframe."""
        groups = data[group_col].unique()
        if len(groups) != 2:
            return {"error": "T-test requires exactly two groups."}
        
        group1 = data[data[group_col] == groups[0]][value_col]
        group2 = data[data[group_col] == groups[1]][value_col]
        
        t_stat, p_val = ttest_ind(group1, group2, nan_policy='omit')
        return {"t_statistic": t_stat, "p_value": p_val}

class VisualizationTool:
    """
    Tool for generating visualizations from data.
    Provides methods for histograms, scatter plots, and heatmaps.
    """
    def __init__(self, name: str = "VisualizationTool", output_dir: str = "charts"):
        self.name = name
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        sns.set_theme()

    def _save_plot_to_file(self, plot_name: str) -> str:
        """Saves the current plot to a file and returns the path."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.output_dir, f"{plot_name}_{timestamp}.png")
        plt.savefig(file_path, format='png', bbox_inches='tight')
        plt.close()
        return file_path

    def plot_histogram(self, data: pd.DataFrame, column: str) -> str:
        """Generates a histogram for a given column and saves it."""
        plt.figure(figsize=(10, 6))
        sns.histplot(data=data, x=column, kde=True)
        plt.title(f"Histogram of {column}")
        return self._save_plot_to_file(f"histogram_{column}")

    def plot_scatter(self, data: pd.DataFrame, x_col: str, y_col: str) -> str:
        """Generates a scatter plot for two columns and saves it."""
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=data, x=x_col, y=y_col)
        plt.title(f"Scatter Plot of {y_col} vs. {x_col}")
        return self._save_plot_to_file(f"scatter_{x_col}_vs_{y_col}")

    def plot_heatmap(self, data: pd.DataFrame) -> str:
        """Generates a heatmap of the correlation matrix and saves it."""
        plt.figure(figsize=(12, 8))
        numeric_df = data.select_dtypes(include=['number'])
        corr = numeric_df.corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title("Correlation Heatmap")
        return self._save_plot_to_file("correlation_heatmap")
