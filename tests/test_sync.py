import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]


def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/(name+'.py'))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ToolkitSync(unittest.TestCase):
    def test_path_escape_is_rejected_before_network_or_mutation(self):
        module=load('sync_toolkit')
        with patch.object(module,'api') as api, self.assertRaises(ValueError):
            module.refresh({'upstream':'sympy/sympy','path':'../outside'})
        api.assert_not_called()

    def test_default_branch_and_hash_validation(self):
        module=load('sync_toolkit')
        item={'upstream':'sympy/sympy','path':'mathematics/sympy','commit':'a'*40}
        replies=[{'private':False,'default_branch':'master'}, {'object':{'type':'commit','sha':'b'*40}}]
        with patch.object(module,'api',side_effect=replies):
            self.assertEqual(module.refresh(item)['commit'],'b'*40)

    def test_noop_preserves_timestamp_and_index(self):
        module=load('sync_toolkit')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            item={'upstream':'sympy/sympy','path':'mathematics/sympy','commit':'a'*40}
            content=json.dumps({'captured_at_utc':'unchanged','repositories':[item]})
            (root/'toolkit-lock.json').write_text(content,encoding='utf-8')
            with patch.object(module,'ROOT',root), patch.object(module,'refresh',return_value=item), patch.object(module,'git') as git, patch.object(sys,'argv',['sync_toolkit.py']):
                module.main()
                git.assert_not_called()
            self.assertEqual((root/'toolkit-lock.json').read_text(encoding='utf-8'),content)

    def test_gitlink_update_works_without_an_upstream_checkout(self):
        module=load('sync_toolkit')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            subprocess.run(['git','init',str(root)],check=True,capture_output=True)
            old={'upstream':'sympy/sympy','path':'mathematics/sympy','commit':'a'*40}
            new=dict(old,commit='b'*40,default_branch='master')
            (root/'toolkit-lock.json').write_text(json.dumps({'repositories':[old]}),encoding='utf-8')
            with patch.object(module,'ROOT',root), patch.object(module,'refresh',return_value=new), patch.object(sys,'argv',['sync_toolkit.py']):
                module.main()
            staged=subprocess.check_output(['git','ls-files','--stage'],cwd=root,text=True)
            self.assertIn('160000 '+'b'*40,staged)
            self.assertEqual(json.loads((root/'toolkit-lock.json').read_text())['repositories'][0]['commit'],'b'*40)


class QuantumlibSync(unittest.TestCase):
    def test_upstream_disappearance_retains_previous_pin(self):
        module=load('sync_quantumlib')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            item={'name':'retained','path':'quantumlib/retained','commit':'a'*40}
            content=json.dumps({'repositories':[item]})
            (root/'quantumlib-lock.json').write_text(content,encoding='utf-8')
            with patch.object(module,'ROOT',root), patch.object(module,'public_repositories',return_value=[]), patch.object(module,'git') as git, patch.object(sys,'argv',['sync_quantumlib.py','--dry-run']):
                module.main()
                git.assert_not_called()
            self.assertEqual((root/'quantumlib-lock.json').read_text(),content)
