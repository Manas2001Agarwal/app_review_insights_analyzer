# Clustering Report - INDmoney Reviews

We analyzed 115 reviews using BERTopic with K-Means clustering (5 topics) and Groq (`openai/gpt-oss-120b`) for labeling.

## Top 5 Themes Identified

### Topic 0: App Performance & Glitches
**Label**: App glitches and crashes
**Keywords**: app, working, open, update, crash, glitches, slow, loading, screen, smooth
**Representative Reviews**:
- "I am trying to Open this app since from last morning but not opening, I am regularly using this app. I am not able to track my stock and Trade"
- "Transfer failed today and show download leaste app i update leaste app but not working"
- "After update this app is now even worse, I hit the buy button on any ticker and the app crashes"

### Topic 1: Customer Support & KYC
**Label**: Poor customer support & KYC
**Keywords**: customer, support, service, kyc, response, care, team, bad, ticket, email
**Representative Reviews**:
- "INDmoney has the worst customer service Ive ever seen. My deposit has been stuck for 20 days... kept giving copypaste replies."
- "There is no call in the helpline number. I have blocked the account and deleted it forever."
- "we are not mad, trying to do kyc but everytime there is technical error you should improve the app."

### Topic 2: Hidden Charges & US Stocks
**Label**: High hidden charges & fees
**Keywords**: charges, money, us, stock, hidden, exchange, conversion, brokerage, high, gst
**Representative Reviews**:
- "Huge charges, exchange rates are higher plus bank charges you additional on exchange rates Average 25 are gone in charges only"
- "Ill admit, INDmoney has a really attractive and userfriendly interface... But what really disappointed me is their claim of no hidden charges."
- "us stock adding money conversion charges are very high compared to Real exchange rate."

### Topic 3: Feature Requests (Tracking)
**Label**: Missing tracking features (LIC/EPF)
**Keywords**: tracking, track, lic, feature, xirr, returns, portfolio, sip, profit, loss
**Representative Reviews**:
- "Need to track Lic policy ..when this feature will be added?"
- "please give a clear xirr button... I cant find my xirr returns for stocks.."
- "Why my tracker only showing Bank? Where is EPF and EPS?"

### Topic 4: Login & Account Access
**Label**: Login issues after number change
**Keywords**: login, account, number, id, email, sign, gmail, previous, help, mobile
**Representative Reviews**:
- "I need to change my number and add another account but there is no option there, I cant even delete my account to log in again with another number."
- "unable to login kindly help me. The problem is all about my previous gmail account which is not available"
- "i forget my previous mobile no. i cant login on app can you help me to login with email id"

## Methodology
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (Local fallback due to API limits).
- **Clustering**: K-Means (k=5) on UMAP-reduced vectors.
- **Labeling**: Groq (`openai/gpt-oss-120b`).
