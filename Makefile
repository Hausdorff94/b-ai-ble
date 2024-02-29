include .env

test_env_vars:
	@echo "BIBLE_VERSION: $(BIBLE_VERSION)"

    
call_api:
	curl -s -H "api-key: $(API_KEY)" "https://api.scripture.api.bible/v1/bibles/$(BIBLE_VERSION)/search?query=david" | jq ".data.verses"
    