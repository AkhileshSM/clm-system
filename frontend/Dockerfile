FROM node:20

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y python3 build-essential && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package*.json ./

# Install dependencies inside the image so native optional packages match Linux.
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
