@flow
def ml_workflow():
    model = train_model(X_train, X_test, y_train)
    predictions = get_prediction(X_test, model)
    evaluate_model(y_test, predictions)

if __name__ == "__main__":
    ml_workflow()

"""
A Prefect Flow is a Python function decorated with the @flow decorator that encapsulates workflow logic. This makes it easier for users to define, 
configure, and execute complex data pipelines with flexibility and ease.
In the code below, we have created a Flow using the @flow decorator. The flow will run all the tasks sequentially, taking inputs from one to another.
"""