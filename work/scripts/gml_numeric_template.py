"""Compile three or four values between fixed, source-attested separators."""

def compile_numeric_template(item,lit):
    parts,ru=item['parts'],item['ru_parts']
    count=len(parts)-1
    assert count in (3,4) and len(ru)==len(parts),item
    assert all(parts[1:-1]),item
    pre,post=parts[0],parts[-1]
    condition=(f'string_pos({lit(pre)},s)==1 && ' if pre else '')
    condition+=f'string_length(s)>={sum(map(len,parts))+count}'
    if post:condition+=f' && string_copy(s,string_length(s)-{len(post)-1},{len(post)})=={lit(post)}'
    lines=['if ('+condition+') {',f'tail=string_copy(s,{len(pre)+1},string_length(s)-{len(pre)+len(post)});']
    values=[f'count_value{i}' for i in range(count)]
    for i,separator in enumerate(parts[1:-1]):
        lines += [f'p=string_pos({lit(separator)},tail);','if (p>1) {',
                  f'{values[i]}=string_copy(tail,1,p-1);',
                  f'tail=string_delete(tail,1,p+{len(separator)-1});']
    lines.append(f'{values[-1]}=tail;')
    numeric=' && '.join(f'(string_length({v})>0'+(f' && string_digits({v})=={v})' if item.get('numeric') else ')') for v in values)
    translated=[f'homd_ru_text({v})' for v in values] if item.get('translate_values') else values
    expression=lit(ru[0])+''.join('+'+v+'+'+lit(r) for v,r in zip(translated,ru[1:]))
    lines += [f'if ({numeric}) return {expression};']+['}']*count
    return lines
