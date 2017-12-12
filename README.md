# Function timeout

For killing python long running tasks when alarm syngal won't help.
Decorator allows you to kill process max in 15 seconds after timeout expires. 
Such big time conditioned by the fact that decorator doing some tries to terminate process gracefully, before killing it with SIGKILL.

Usage 

```python
from ftimout import timeout
from time import sleep

# 20 minutes
@timeout(20 * 60)
def long_function():
    while True:
    	sleep(10)
        print "Next loop"
```
