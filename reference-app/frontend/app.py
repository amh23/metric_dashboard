from flask import Flask, render_template, request
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics

from jaeger_client import Config
from flask_opentracing import FlaskTracing

app = Flask(__name__)
#jaeger
config = Config(
    config={
        'sampler':
        {'type': 'const',
         'param': 1},
                        'logging': True,
                        'reporter_batch_size': 1,}, 
                        service_name="service_frontend")
jaeger_tracer = config.initialize_tracer()
tracing = FlaskTracing(jaeger_tracer, False, app)
#jaeger


metrics = GunicornInternalPrometheusMetrics(app)

@app.route('/')
@tracing.trace()
def homepage():
    return render_template("main.html")


if __name__ == "__main__":
    app.run()
