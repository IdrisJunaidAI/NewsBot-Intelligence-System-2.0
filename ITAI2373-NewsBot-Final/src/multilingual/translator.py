"""Optional translation adapter; never falsely claim offline output is translated."""
class Translator:
    def translate(self,text,source='auto',target='en'):
        if source==target:return {'available':True,'text':text,'provider':'identity','source':source,'target':target}
        try:
            from deep_translator import GoogleTranslator
        except ImportError:
            return {'available':False,'text':None,'reason':'Install deep-translator and enable network access for translation',
                    'source':source,'target':target}
        try:
            translated=GoogleTranslator(source=source,target=target).translate(text[:4500])
            return {'available':True,'text':translated,'provider':'GoogleTranslator via deep-translator',
                    'source':source,'target':target,'note':'Subject to provider availability and privacy policy'}
        except Exception as exc:
            return {'available':False,'text':None,'reason':str(exc),'source':source,'target':target}
