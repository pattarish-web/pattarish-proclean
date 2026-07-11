# Build context must be the ops/ directory (sibling of webhook/ and modules/).
FROM node:20-alpine

WORKDIR /app

COPY webhook/package.json webhook/package-lock.json* ./webhook/
WORKDIR /app/webhook
RUN npm install --omit=dev

WORKDIR /app
COPY webhook/src ./webhook/src
COPY modules ./modules

WORKDIR /app/webhook
ENV PORT=3000
ENV NODE_ENV=production
EXPOSE 3000

# src/index.js resolves LIFF HTML at ../../modules → /app/modules
CMD ["node", "src/index.js"]
