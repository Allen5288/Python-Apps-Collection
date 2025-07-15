from logger import logger

def query_chain(chain, user_input:str):
    try:
        logger.debug(f"Processing user input: {user_input}")
        result = chain({"query": user_input})
        response = {
            "response": result["result"],
            "source": [doc.metadata.get("sources", "") for doc in result["source_documents"]]
        }
        logger.debug(f"Query response: {response}")
        return response
    except Exception as e:
        logger.exception(f"Error processing query: {e}")
        raise