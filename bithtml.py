#!/usr/bin/env python3

import os, sys
import fasm
import fasm.output
from prjxray.db import Database
import fasm_disassembler
from prjxray import bitstream
import json

def parse_frame(f):
    words = []

    for line in f:
        l = line.strip()

        for w in l.split(' '):
            words.append(int(w, 16))

            if len(words) >= 101:
                break

        if len(words) >= 101:
            break

    return words


def parse_file(input):
    frames = []

    with open(input, 'r') as f:
        for line in f:
            l = line.strip()
            if l.startswith('.frame'):
                frame = dict()
                frame['address'] = int(l.split(' ')[1], 16)
                frame['data'] = parse_frame(f)
                frames.append(frame)

    return frames


def bit_to_feature(fmap, frame, bitno):
    if frame in fmap.keys():
        if bitno in fmap[frame].keys():
            return fmap[frame][bitno]

    return None


def run(input, output, frames_per_line, features_map):
    frames = parse_file(input)

    col = 0

    out = open(output, 'w')
    out.write("<html><head></head><body>\n")

    # Whole bitstream
    out.write("<h3>Bistream dump:</h3>\n")
    out.write("<table border>\n")
    for f in frames:
        if col == 0:
            out.write(" <tr height=\"20\">\n")

        col += 1
        color = 'white'
        if sum(f['data']):
            color = 'green'

        out.write("  <td width=\"18\" bgcolor=\"{}\" title=\"Frame @ {}\">".format(
            color,
            '0x%08x' % f['address']
        ))

        if sum(f['data']):
            out.write('<a href="#{}">F</a>'.format('%08x' % f['address']))

        out.write("</td>\n")

        if col >= frames_per_line:
            out.write(" </tr>\n")
            col = 0

    out.write("</table>\n")

    # Non-zero frames
    for f in frames:
        if sum(f['data']) == 0:
           continue

        out.write('<h3>Frame {}:\n'.format('0x%08x' % f['address']))
        out.write('<table border id="{}">\n'.format('%08x' % f['address']))
        col = 0
        for i in range(101 * 32):
            if col == 0:
                out.write(" <tr height=\"20\">\n")

            col += 1
            color = 'white'
            feat = ''

            feature = bit_to_feature(features_map, f['address'], i)
            if feature:
                color = 'green'
                feat = feature['feature'] + ' @ ' + feature['tile']

            out.write("  <td width=\"18\" bgcolor=\"{}\" title=\"Bit {}: {}_{} ({})\"></td>\n".format(
                color,
                str(i),
                str(i // 32), str(i - (i // 32) * 32),
                feat
            ))

            if col >= frames_per_line:
                out.write(" </tr>\n")
                col = 0

        out.write('</table>\n')

    out.write("</body></html>\n")
    out.close()


def run_vue(input, output, frames_per_line, features_map):
    frames = parse_file(input)

    out = open(output, 'w')
    out.write('{ "data": [\n')

    series = []
    serie = ""

    col = 0
    lineno = 1
    for f in frames:
        if col == 0:
            serie = '  {{ "name": {}, "data": ['.format(lineno)

        col += 1

        # Scale frame usage
        nz = 0
        for n in f['data']:
            if n: nz += bin(n).count('1')

        _nz = ((100 * nz)//(101 * 32))//10
        if nz > 0 and _nz == 0:
            nz = 1
        else:
            nz = _nz
        nz += 1

        #out.write("{{ x: {}, y: {} }},".format(str(col), str(nz)))
        serie += '{{ "x": {}, "y": {}, "address": "{}" }},'.format(str(col), str(nz), '0x%08x' % f['address'])

    #    if sum(f['data']):
    #        out.write('<a href="#{}">F</a>'.format('%08x' % f['address']))


        if col >= frames_per_line:
            serie = serie[:-1]
            serie += "]},\n"
            series.append(serie)
            col = 0
            lineno += 1

    serie = serie[:-1]
    if col > 0 and col < frames_per_line:
        serie += "]},\n"
        series.append(serie)

    for s in reversed(series):
        out.write(s)

    # End of series
    out.write("{}]}\n")
    out.close()

    # Non-zero frames
    itr = 0
    for f in frames:
        itr += 1
        if itr % 10 == 0:
            sys.stdout.write('Dumping frames: ' + str(itr) + ' / ' + str(len(frames)) + '\r')
            sys.stdout.flush()
        #if sum(f['data']) == 0:
        #   continue

        lineno = 1
        series = []
        out = open('frames/frame_' + ('0x%08x' % f['address']) + '.json', 'w')
        out.write('{ "data": [\n')

        col = 0
        for i in range(100 * 32):
            if col == 0:
                serie = '      {{ "name": {}, "data": ['.format(lineno)

            col += 1

            feat = 'not used'
            nz = 1
            feature = bit_to_feature(features_map, f['address'], i)
            if feature:
                color = 'green'
                feat = feature['feature'] + ' @ ' + feature['tile']
                nz = 11

            #    out.write("  <td width=\"18\" bgcolor=\"{}\" title=\"Bit {}: {}_{} ({})\"></td>\n".format(
            #        color,
            #        str(i),
            #        str(i // 32), str(i - (i // 32) * 32),
            #        feat
            #    ))

            serie += '{{ "x": {}, "y": {}, "feature": "{}" }}'.format(str(col-1), str(nz), feat)

            if col >= (32 * 2):
                serie += ']},\n'
                series.append(serie)
                col = 0
                lineno += 1
            else:
                serie += ','

        # Append 101 word
        #serie += ']},\n'
        #series.append(serie)

        for s in reversed(series):
            out.write(s)

        out.write('{}]}\n')
        out.close()


def bits_to_fasm(db_root, bits_file):
    db = Database(db_root)
    grid = db.grid()
    disassembler = fasm_disassembler.FasmDisassembler(db)

    with open(bits_file) as f:
        bitdata = bitstream.load_bitdata(f)

    features_map = []

    model = fasm.output.merge_and_sort(
        disassembler.find_features_in_bitstream(bitdata, fmap=features_map, verbose=True),
        zero_function=disassembler.is_zero_feature,
        sort_key=grid.tile_key,
    )

    features_map_dict = dict()

    for f in features_map:
        if len(f['bit']) == 0:
            continue

        for b in f['bit']:
            s = b.split('_')
            addr = int(s[1], 16)
            features_map_dict[addr] = dict()

    for f in features_map:
        if len(f['bit']) == 0:
            continue

        for b in f['bit']:
            s = b.split('_')
            addr = int(s[1], 16)
            word = int(s[2])
            bit  = int(s[3])
            bitno = (word * 32) + bit
            features_map_dict[addr][bitno] = f

    return features_map_dict


def grid_size(db_dir):
    tilegrid = ''
    with open(db_dir + '/tilegrid.json', 'r') as f:
        data = f.read()
        tilegrid = json.loads(data)

    min_x =  9999
    max_x = -9999
    min_y =  9999
    max_y = -9999

    for t in tilegrid:
        #if not t.startswith('CLB'): continue

        x = int(t.split('_X')[1].split('Y')[0])
        y = int(t.split('_X')[1].split('Y')[1])

        if x < min_x: min_x = x
        if x > max_x: max_x = x
        if y < min_y: min_y = y
        if y > max_y: max_y = y

    #print('Grid: X: ' + str(min_x) + ' - ' + str(max_x) + ' , Y: ' + str(min_y) + ' - ' + str(max_y))
    return min_x, max_x, min_y, max_y


def run_dump_grid(db_dir, bits, output, grid_dir):
    # Calculate grid size
    min_x, max_x, min_y, max_y = grid_size(db_dir)

    # Empty grid
    grid = [[[] for j in range(min_y, max_y + 1)] for i in range(min_x, max_x + 1)]

    # Map features to grid
    fmap = bits_to_fasm(db_dir, bits)

    for k in fmap.keys():
        for j in fmap[k].keys():
            f = fmap[k][j]

            if f['feature'] == 'unknown':
                print('unknown bit: ' + str(f))
                u = int(f['bit'][0].split('_')[1], 16)
                frame = (u >> 16) & 0xffffffff
                row = (frame >> 17) & 0x1f
                column = (frame >> 7) & 0x3ff

                #print(': ' + ('0x%08x' % frame) + ' - ' + str(column) + ' x ' + str(row))
                #grid[row][column] = -1

                tmp = dict()
                tmp['bit'] = f['bit']
                grid[row][column].append(tmp)

            else:
                tile = f['tile']
                x = int(tile.split('_X')[1].split('Y')[0])
                y = int(tile.split('_X')[1].split('Y')[1])

                tmp = dict()
                tmp['feature'] = f
                grid[x - min_x][y - min_y].append(tmp)


    # Limit grid size for debugging
    #max_x = min_x + 10
    #max_y = min_y + 10


    # Fill grid info
    grid_y_data = []
    for y in range(min_y, max_y + 1):
        grid_x_data = []

        for x in range(min_x, max_x + 1):
            t = dict()
            t['x'] = x

            t['y'] = 0

            if len(grid[x - min_x][y - min_y]):
                t['y'] = 1

                bitfeat = []
                for b in grid[x - min_x][y - min_y]:
                    if 'feature' not in b.keys():
                        t['y'] = -1
                        tmp = dict()
                        tmp['bitname'] = b['bit']
                        tmp['feature'] = 'unknown'
                        bitfeat.append(tmp)
                    else:
                        tmp = dict()
                        tmp['bitname'] = b['feature']['bit'][0]
                        tmp['feature'] = b['feature']['feature']
                        bitfeat.append(tmp)

                with open('grid/grid_{}_{}.json'.format(x, y), 'w') as fp:
                    json.dump(bitfeat, fp, indent=2)

            #    print('grid: ' + str(x) + 'x' + str(y) + ' : ' + str(t['y']))
            t['address'] = '{} x {}'.format(x, y)

            grid_x_data.append(t)

        grid_x = dict()
        grid_x['name'] = int(y)
        grid_x['data'] = grid_x_data
        grid_y_data.append(grid_x)

    grid_y = dict()
    grid_y['data'] = grid_y_data

    with open(output, 'w') as fp: json.dump(grid_y, fp, indent=2)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate HTML of bitstream.")
    parser.add_argument(
        "--frames",
        default=None,
        help='Read bitread report from file'
    )
    parser.add_argument(
        "--bits",
        default=None,
        help='Read bitread report from file'
    )
    parser.add_argument(
        "--html",
        default=None,
        help='Dump html to file'
    )
    parser.add_argument(
        "--frames-per-line",
        default="94",
        help="Frames per line",
    )
    parser.add_argument(
        "--db-dir",
        help="Database directory",
    )
    parser.add_argument(
        "--vue",
        default=None,
        help='Dump in Vue.js format'
    )
    parser.add_argument(
        "--dump-grid",
        default=None,
        help='Dump FPGA grid usage to JSON'
    )
    parser.add_argument(
        "--grid-dir",
        default=None,
        help="Directory to dump grid cells info"
    )

    args = parser.parse_args()

    if args.html or args.vue:
        fmap = bits_to_fasm(args.db_dir, args.bits)

        if args.html:
            run(
                input=args.frames,
                output=args.html,
                frames_per_line=int(args.frames_per_line, 10),
                features_map=fmap,
            )

        if args.vue:
            run_vue(
                input=args.frames,
                output=args.vue,
                frames_per_line=int(args.frames_per_line, 10),
                features_map=fmap,
            )

    if args.dump_grid:
        run_dump_grid(
            db_dir=args.db_dir,
            bits=args.bits,
            output=args.dump_grid,
            grid_dir=args.grid_dir,
        )


if __name__ == "__main__":
    main()
