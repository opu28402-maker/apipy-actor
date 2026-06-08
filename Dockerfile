# Apify's Python Actor base image
FROM apify/actor-python:3.12

# Working directory set korchi
WORKDIR /usr/src/app

# requirements আগে copy করে install করা হচ্ছে
# (Docker cache ব্যবহার করার জন্য)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# বাকি সব files copy করা হচ্ছে
COPY . ./

# Actor run করার command
CMD ["python", "-m", "src.main"]
