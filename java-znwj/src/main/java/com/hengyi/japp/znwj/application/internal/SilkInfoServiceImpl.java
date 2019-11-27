package com.hengyi.japp.znwj.application.internal;

import com.github.benmanes.caffeine.cache.Caffeine;
import com.github.benmanes.caffeine.cache.LoadingCache;
import com.github.benmanes.caffeine.cache.RemovalCause;
import com.google.inject.Inject;
import com.google.inject.Singleton;
import com.google.inject.name.Named;
import com.hengyi.japp.znwj.application.SilkInfoService;
import com.hengyi.japp.znwj.domain.SilkInfo;
import com.hengyi.japp.znwj.interfaces.python.DetectResult;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collection;

import static com.github.ixtf.japp.core.Constant.YAML_MAPPER;
import static com.hengyi.japp.znwj.Constant.*;

/**
 * @author jzb 2019-11-21
 */
@Slf4j
@Singleton
public class SilkInfoServiceImpl implements SilkInfoService {
    private final Path dbPath;
    private final LoadingCache<String, SilkInfo> silkCache;

    @Inject
    private SilkInfoServiceImpl(@Named("silkCacheSpec") String spec, @Named("dbPath") Path dbPath) {
        this.dbPath = dbPath;
        silkCache = Caffeine.from(spec).removalListener((String key, SilkInfo value, RemovalCause cause) -> {
            saveDisk(value);
        }).build(code -> {
            final Path path = silkFile(code);
            if (Files.exists(path)) {
                return YAML_MAPPER.readValue(path.toFile(), SilkInfo.class);
            }
            final SilkInfo silkInfo = new SilkInfo();
            silkInfo.setCode(code);
            return silkInfo;
        });
    }

    @Override
    public SilkInfo add(DetectResult detectResult) {
        return null;
    }

    private Path silkFile(String code) {
        return dbPath.resolve(code).resolve(SILK_INFO_YML);
    }

    @SneakyThrows(IOException.class)
    private void saveDisk(SilkInfo silkInfo) {
        final File silkFile = silkFile(silkInfo.getCode()).toFile();
        FileUtils.forceMkdirParent(silkFile);
        YAML_MAPPER.writeValue(silkFile, silkInfo);
    }

    private Path originalDir(String code) {
        return silkFile(code).getParent().resolve(ORIGINAL_DIR);
    }

    @Override
    public Path detectDir(String code) {
        return silkFile(code).getParent().resolve(DETECT_DIR);
    }

    @Override
    public SilkInfo find(String code) {
        return silkCache.get(code);
    }

    @Override
    public Collection<SilkInfo> list() {
        return silkCache.asMap().values();
    }

    @Override
    public void cleanUp() {
        silkCache.asMap().values().forEach(this::saveDisk);
        silkCache.cleanUp();
    }

}
